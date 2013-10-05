#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
#
# This file is part of Eos.
#
# Eos is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Eos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Eos. If not, see <http://www.gnu.org/licenses/>.
#===============================================================================


from unittest.mock import Mock

from eos.const.eos import State
from eos.fit.holder.container import HolderRestrictedSet
from eos.fit.holder.item import Booster, Skill
from eos.tests.fit.fitTestCase import FitTestCase


class TestContainerRestrictedSet(FitTestCase):

    def makeFit(self, *args, **kwargs):
        fit = super().makeFit(*args, **kwargs)
        fit.container = HolderRestrictedSet(fit, Skill)
        return fit

    def customMembershipCheck(self, fit, holder):
        self.assertIn(holder, fit.container)

    def testDetachedAddNone(self):
        fit = self.makeFit()
        # Action
        self.assertRaises(TypeError, fit.container.add, None)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        # Misc
        self.assertFitBuffersEmpty(fit.container)

    def testDetachedAddHolder(self):
        fit = self.makeFit()
        holder = Mock(_fit=None, _typeId=1, state=State.offline, spec_set=Skill)
        # Action
        fit.container.add(holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 1)
        self.assertIs(fit.container[1], holder)
        self.assertIn(holder, fit.container)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.container.remove(holder)
        self.assertFitBuffersEmpty(fit.container)

    def testDetachedAddHolderTypeFailure(self):
        fit = self.makeFit()
        holder = Mock(_fit=None, _typeId=1, state=State.offline, spec_set=Booster)
        # Action
        self.assertRaises(TypeError, fit.container.add, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assertFitBuffersEmpty(fit.container)

    def testDetachedAddHolderValueFailureHasFit(self):
        fit = self.makeFit()
        fitOther = self.makeFit()
        holder = Mock(_fit=None, _typeId=1, state=State.overload, spec_set=Skill)
        fitOther.container.add(holder)
        # Action
        self.assertRaises(ValueError, fit.container.add, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertEqual(len(fitOther.lt), 0)
        self.assertEqual(len(fitOther.rt), 0)
        self.assertEqual(len(fitOther.st), 0)
        self.assertEqual(len(fitOther.container), 1)
        self.assertIs(fitOther.container[1], holder)
        self.assertIn(holder, fitOther.container)
        self.assertIs(holder._fit, fitOther)
        # Misc
        fitOther.container.remove(holder)
        self.assertFitBuffersEmpty(fit.container)
        self.assertFitBuffersEmpty(fitOther.container)

    def testDetachedAddHolderValueFailureExistingTypeId(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, _typeId=1, state=State.offline, spec_set=Skill)
        holder2 = Mock(_fit=None, _typeId=1, state=State.offline, spec_set=Skill)
        fit.container.add(holder1)
        # Action
        self.assertRaises(ValueError, fit.container.add, holder2)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 1)
        self.assertIs(fit.container[1], holder1)
        self.assertIn(holder1, fit.container)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        # Misc
        fit.container.remove(holder1)
        self.assertFitBuffersEmpty(fit.container)

    def testDetachedRemoveHolder(self):
        fit = self.makeFit()
        holder = Mock(_fit=None, _typeId=1, state=State.active, spec_set=Skill)
        fit.container.add(holder)
        # Action
        fit.container.remove(holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assertFitBuffersEmpty(fit.container)

    def testDetachedRemoveHolderFailure(self):
        fit = self.makeFit()
        holder = Mock(_fit=None, _typeId=1, state=State.overload, spec_set=Skill)
        # Action
        self.assertRaises(KeyError, fit.container.remove, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assertFitBuffersEmpty(fit.container)

    def testDetachedClear(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, _typeId=1, state=State.active, spec_set=Skill)
        holder2 = Mock(_fit=None, _typeId=2, state=State.online, spec_set=Skill)
        fit.container.add(holder1)
        fit.container.add(holder2)
        # Action
        fit.container.clear()
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit.container)

    def testAttachedAddNone(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        # Action
        self.assertRaises(TypeError, fit.container.add, None)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        # Misc
        self.assertFitBuffersEmpty(fit.container)

    def testAttachedAddHolder(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder = Mock(_fit=None, _typeId=1, state=State.online, spec_set=Skill)
        # Action
        fit.container.add(holder)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder, fit.lt)
        self.assertEqual(fit.lt[holder], {State.offline, State.online})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder, fit.rt)
        self.assertEqual(fit.rt[holder], {State.offline, State.online})
        self.assertEqual(len(fit.st), 1)
        self.assertIn(holder, fit.st)
        self.assertEqual(fit.st[holder], {State.offline, State.online})
        self.assertEqual(len(fit.container), 1)
        self.assertIs(fit.container[1], holder)
        self.assertIn(holder, fit.container)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.container.remove(holder)
        self.assertFitBuffersEmpty(fit.container)

    def testAttachedAddHolderTypeFailure(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder = Mock(_fit=None, _typeId=1, state=State.offline, spec_set=Booster)
        # Action
        self.assertRaises(TypeError, fit.container.add, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assertFitBuffersEmpty(fit.container)

    def testAttachedAddHolderValueFailureHasFit(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        fitOther = self.makeFit(eos=eos)
        holder = Mock(_fit=None, _typeId=1, state=State.offline, spec_set=Skill)
        fitOther.container.add(holder)
        # Action
        self.assertRaises(ValueError, fit.container.add, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertEqual(len(fitOther.lt), 1)
        self.assertIn(holder, fitOther.lt)
        self.assertEqual(fitOther.lt[holder], {State.offline})
        self.assertEqual(len(fitOther.rt), 1)
        self.assertIn(holder, fitOther.rt)
        self.assertEqual(fitOther.rt[holder], {State.offline})
        self.assertEqual(len(fitOther.st), 1)
        self.assertIn(holder, fitOther.st)
        self.assertEqual(fitOther.st[holder], {State.offline})
        self.assertEqual(len(fitOther.container), 1)
        self.assertIs(fitOther.container[1], holder)
        self.assertIn(holder, fitOther.container)
        self.assertIs(holder._fit, fitOther)
        # Misc
        fitOther.container.remove(holder)
        self.assertFitBuffersEmpty(fit.container)
        self.assertFitBuffersEmpty(fitOther.container)

    def testAttachedAddHolderValueFailureExistingTypeId(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder1 = Mock(_fit=None, _typeId=1, state=State.offline, spec_set=Skill)
        holder2 = Mock(_fit=None, _typeId=1, state=State.offline, spec_set=Skill)
        fit.container.add(holder1)
        # Action
        self.assertRaises(ValueError, fit.container.add, holder2)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline})
        self.assertEqual(len(fit.st), 1)
        self.assertIn(holder1, fit.st)
        self.assertEqual(fit.st[holder1], {State.offline})
        self.assertEqual(len(fit.container), 1)
        self.assertIs(fit.container[1], holder1)
        self.assertIn(holder1, fit.container)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        self.assertIs(fit.container[1], holder1)
        # Misc
        fit.container.remove(holder1)
        self.assertFitBuffersEmpty(fit.container)

    def testAttachedRemoveHolder(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder = Mock(_fit=None, _typeId=1, state=State.overload, spec_set=Skill)
        fit.container.add(holder)
        # Action
        fit.container.remove(holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assertFitBuffersEmpty(fit.container)

    def testAttachedRemoveHolderFailure(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder = Mock(_fit=None, _typeId=1, state=State.online, spec_set=Skill)
        # Action
        self.assertRaises(KeyError, fit.container.remove, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assertFitBuffersEmpty(fit.container)

    def testAttachedClear(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder1 = Mock(_fit=None, _typeId=1, state=State.overload, spec_set=Skill)
        holder2 = Mock(_fit=None, _typeId=2, state=State.active, spec_set=Skill)
        fit.container.add(holder1)
        fit.container.add(holder2)
        # Action
        fit.container.clear()
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit)

    def testGetItem(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder = Mock(_fit=None, _typeId=5, state=State.online, spec_set=Skill)
        fit.container.add(holder)
        self.assertIs(fit.container[5], holder)
        self.assertRaises(KeyError, fit.container.__getitem__, 0)
        self.assertRaises(KeyError, fit.container.__getitem__, 6)
        fit.container.remove(holder)
        self.assertFitBuffersEmpty(fit.container)

    def testLen(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, _typeId=1, state=State.active, spec_set=Skill)
        holder2 = Mock(_fit=None, _typeId=2, state=State.online, spec_set=Skill)
        self.assertEqual(len(fit.container), 0)
        fit.container.add(holder1)
        self.assertEqual(len(fit.container), 1)
        fit.container.add(holder2)
        self.assertEqual(len(fit.container), 2)
        fit.container.remove(holder1)
        self.assertEqual(len(fit.container), 1)
        fit.container.remove(holder2)
        self.assertEqual(len(fit.container), 0)
        self.assertObjectBuffersEmpty(fit)

    def testContains(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, _typeId=1, state=State.active, spec_set=Skill)
        holder2 = Mock(_fit=None, _typeId=2, state=State.offline, spec_set=Skill)
        self.assertFalse(holder1 in fit.container)
        self.assertFalse(holder2 in fit.container)
        fit.container.add(holder1)
        self.assertTrue(holder1 in fit.container)
        self.assertFalse(holder2 in fit.container)
        fit.container.add(holder2)
        self.assertTrue(holder1 in fit.container)
        self.assertTrue(holder2 in fit.container)
        fit.container.remove(holder1)
        self.assertFalse(holder1 in fit.container)
        self.assertTrue(holder2 in fit.container)
        fit.container.remove(holder2)
        self.assertFalse(holder1 in fit.container)
        self.assertFalse(holder2 in fit.container)
        self.assertObjectBuffersEmpty(fit)

    def testIter(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, _typeId=1, state=State.active, spec_set=Skill)
        holder2 = Mock(_fit=None, _typeId=2, state=State.offline, spec_set=Skill)
        self.assertEqual(set(holder for holder in fit.container), set())
        fit.container.add(holder1)
        self.assertEqual(set(holder for holder in fit.container), {holder1})
        fit.container.add(holder2)
        self.assertEqual(set(holder for holder in fit.container), {holder1, holder2})
        fit.container.remove(holder1)
        self.assertEqual(set(holder for holder in fit.container), {holder2})
        fit.container.remove(holder2)
        self.assertEqual(set(holder for holder in fit.container), set())
        self.assertObjectBuffersEmpty(fit)
