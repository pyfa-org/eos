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
from eos.fit.holder.container import HolderList
from eos.fit.holder.item import Booster, Implant
from eos.tests.fit.fitTestCase import FitTestCase


class TestContainerOrderedEquip(FitTestCase):

    def makeFit(self, *args, **kwargs):
        fit = super().makeFit(*args, **kwargs)
        fit.container = HolderList(fit, Implant)
        return fit

    def customMembershipCheck(self, fit, holder):
        self.assertIn(holder, fit.container)

    def testDetachedNoneToEmpty(self):
        fit = self.makeFit()
        # Action
        self.assertRaises(TypeError, fit.container.equip, None)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        # Misc
        self.assertObjectBuffersEmpty(fit.container)

    def testDetachedHolderToEmpty(self):
        fit = self.makeFit()
        holder = Mock(_fit=None, state=State.offline, spec_set=Implant)
        # Action
        fit.container.equip(holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], holder)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.container.remove(holder)
        self.assertObjectBuffersEmpty(fit.container)

    def testDetachedHolderToEmptyTypeFailure(self):
        fit = self.makeFit()
        holder = Mock(_fit=None, state=State.offline, spec_set=Booster)
        # Action
        self.assertRaises(TypeError, fit.container.equip, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit.container)

    def testDetachedHolderToEmptyValueFailure(self):
        fit = self.makeFit()
        fitOther = self.makeFit()
        holder = Mock(_fit=None, state=State.active, spec_set=Implant)
        fitOther.container.equip(holder)
        # Action
        self.assertRaises(ValueError, fit.container.equip, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        self.assertEqual(len(fitOther.lt), 0)
        self.assertEqual(len(fitOther.rt), 0)
        self.assertEqual(len(fitOther.st), 0)
        self.assertIs(len(fitOther.container), 1)
        self.assertIs(fitOther.container[0], holder)
        self.assertIs(holder._fit, fitOther)
        # Misc
        fitOther.container.remove(holder)
        self.assertObjectBuffersEmpty(fit.container)

    def testDetachedHolderSolid(self):
        # Check case when all slots of list are filled
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.offline, spec_set=Implant)
        holder3 = Mock(_fit=None, state=State.offline, spec_set=Implant)
        fit.container.append(holder1)
        fit.container.append(holder2)
        # Action
        fit.container.equip(holder3)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 3)
        self.assertIs(fit.container[2], holder3)
        self.assertIs(holder3._fit, fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        fit.container.remove(holder3)
        self.assertObjectBuffersEmpty(fit.container)

    def testDetachedHolderFirstHole(self):
        # Check that leftmost empty slot is taken
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.online, spec_set=Implant)
        holder3 = Mock(_fit=None, state=State.overload, spec_set=Implant)
        holder4 = Mock(_fit=None, state=State.online, spec_set=Implant)
        fit.container.append(holder1)
        fit.container.insert(3, holder2)
        fit.container.insert(6, holder3)
        # Action
        fit.container.equip(holder4)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 7)
        self.assertIs(fit.container[1], holder4)
        self.assertIs(holder4._fit, fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        fit.container.remove(holder3)
        fit.container.remove(holder4)
        self.assertObjectBuffersEmpty(fit.container)

    def testAttachedNoneToEmpty(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        # Action
        self.assertRaises(TypeError, fit.container.equip, None)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        # Misc
        self.assertObjectBuffersEmpty(fit.container)

    def testAttachedHolderToEmpty(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder = Mock(_fit=None, state=State.overload, spec_set=Implant)
        # Action
        fit.container.equip(holder)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder, fit.lt)
        self.assertEqual(fit.lt[holder], {State.offline, State.online, State.active, State.overload})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder, fit.rt)
        self.assertEqual(fit.rt[holder], {State.offline, State.online, State.active, State.overload})
        self.assertEqual(len(fit.st), 1)
        self.assertIn(holder, fit.st)
        self.assertEqual(fit.st[holder], {State.offline, State.online, State.active, State.overload})
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], holder)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.container.remove(holder)
        self.assertObjectBuffersEmpty(fit.container)

    def testAttachedHolderToEmptyTypeFailure(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder = Mock(_fit=None, state=State.offline, spec_set=Booster)
        # Action
        self.assertRaises(TypeError, fit.container.equip, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit.container)

    def testAttachedHolderToEmptyValueFailure(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        fitOther = self.makeFit(eos=eos)
        holder = Mock(_fit=None, state=State.offline, spec_set=Implant)
        fitOther.container.equip(holder)
        # Action
        self.assertRaises(ValueError, fit.container.equip, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        self.assertEqual(len(fitOther.lt), 1)
        self.assertIn(holder, fitOther.lt)
        self.assertEqual(fitOther.lt[holder], {State.offline})
        self.assertEqual(len(fitOther.rt), 1)
        self.assertIn(holder, fitOther.rt)
        self.assertEqual(fitOther.rt[holder], {State.offline})
        self.assertEqual(len(fitOther.st), 1)
        self.assertIn(holder, fitOther.st)
        self.assertEqual(fitOther.st[holder], {State.offline})
        self.assertIs(len(fitOther.container), 1)
        self.assertIs(fitOther.container[0], holder)
        self.assertIs(holder._fit, fitOther)
        # Misc
        fitOther.container.remove(holder)
        self.assertObjectBuffersEmpty(fit.container)

    def testAttachedHolderSolid(self):
        # Check case when all slots of list are filled
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.active, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.offline, spec_set=Implant)
        holder3 = Mock(_fit=None, state=State.overload, spec_set=Implant)
        fit.container.append(holder1)
        fit.container.append(holder2)
        # Action
        fit.container.equip(holder3)
        # Checks
        self.assertEqual(len(fit.lt), 3)
        self.assertIn(holder3, fit.lt)
        self.assertEqual(fit.lt[holder3], {State.offline, State.online, State.active, State.overload})
        self.assertEqual(len(fit.rt), 3)
        self.assertIn(holder3, fit.rt)
        self.assertEqual(fit.rt[holder3], {State.offline, State.online, State.active, State.overload})
        self.assertEqual(len(fit.st), 3)
        self.assertIn(holder3, fit.st)
        self.assertEqual(fit.st[holder3], {State.offline, State.online, State.active, State.overload})
        self.assertIs(len(fit.container), 3)
        self.assertIs(fit.container[2], holder3)
        self.assertIs(holder3._fit, fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        fit.container.remove(holder3)
        self.assertObjectBuffersEmpty(fit.container)

    def testAttachedHolderFirstHole(self):
        # Check that leftmost empty slot is taken
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.active, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.offline, spec_set=Implant)
        holder3 = Mock(_fit=None, state=State.online, spec_set=Implant)
        holder4 = Mock(_fit=None, state=State.active, spec_set=Implant)
        fit.container.append(holder1)
        fit.container.insert(3, holder2)
        fit.container.insert(6, holder3)
        # Action
        fit.container.equip(holder4)
        # Checks
        self.assertEqual(len(fit.lt), 4)
        self.assertIn(holder4, fit.lt)
        self.assertEqual(fit.lt[holder4], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 4)
        self.assertIn(holder4, fit.rt)
        self.assertEqual(fit.rt[holder4], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.st), 4)
        self.assertIn(holder4, fit.st)
        self.assertEqual(fit.st[holder4], {State.offline, State.online, State.active})
        self.assertIs(len(fit.container), 7)
        self.assertIs(fit.container[1], holder4)
        self.assertIs(holder4._fit, fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        fit.container.remove(holder3)
        fit.container.remove(holder4)
        self.assertObjectBuffersEmpty(fit.container)
