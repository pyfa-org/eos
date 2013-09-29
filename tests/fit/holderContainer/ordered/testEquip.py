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
from eos.fit.holder import Holder
from eos.fit.holder.container import HolderList
from eos.tests.fit.fitTestCase import FitTestCase


class TestContainerOrderedEquip(FitTestCase):

    def makeFit(self, *args, **kwargs):
        fit = super().makeFit(*args, **kwargs)
        fit.ordered = HolderList(fit)
        return fit

    def customMembershipCheck(self, fit, holder):
        self.assertIn(holder, fit.ordered)

    def testDetachedNoneToEmpty(self):
        fit = self.makeFit()
        # Action
        self.assertRaises(TypeError, fit.ordered.equip, None)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.ordered), 0)
        # Misc
        self.assertObjectBuffersEmpty(fit)

    def testDetachedHolderToEmpty(self):
        fit = self.makeFit()
        holder = Mock(_fit=None, state=State.offline, spec_set=Holder)
        # Action
        fit.ordered.equip(holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.ordered), 1)
        self.assertIs(fit.ordered[0], holder)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.ordered.remove(holder)
        self.assertObjectBuffersEmpty(fit)

    def testDetachedHolderToEmptyTypeFailure(self):
        fit = self.makeFit()
        holder = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        # Action
        self.assertRaises(TypeError, fit.ordered.equip, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.ordered), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit)

    def testDetachedHolderToEmptyValueFailure(self):
        fit = self.makeFit()
        fitOther = self.makeFit()
        holder = Mock(_fit=None, state=State.active, spec_set=Holder)
        fitOther.ordered.equip(holder)
        # Action
        self.assertRaises(ValueError, fit.ordered.equip, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.ordered), 0)
        self.assertEqual(len(fitOther.lt), 0)
        self.assertEqual(len(fitOther.rt), 0)
        self.assertEqual(len(fitOther.st), 0)
        self.assertIs(len(fitOther.ordered), 1)
        self.assertIs(fitOther.ordered[0], holder)
        self.assertIs(holder._fit, fitOther)
        # Misc
        fitOther.ordered.remove(holder)
        self.assertObjectBuffersEmpty(fit)

    def testDetachedHolderSolid(self):
        # Check case when all slots of list are filled
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=Holder)
        holder2 = Mock(_fit=None, state=State.offline, spec_set=Holder)
        holder3 = Mock(_fit=None, state=State.offline, spec_set=Holder)
        fit.ordered.append(holder1)
        fit.ordered.append(holder2)
        # Action
        fit.ordered.equip(holder3)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.ordered), 3)
        self.assertIs(fit.ordered[2], holder3)
        self.assertIs(holder3._fit, fit)
        # Misc
        fit.ordered.remove(holder1)
        fit.ordered.remove(holder2)
        fit.ordered.remove(holder3)
        self.assertObjectBuffersEmpty(fit)

    def testDetachedHolderFirstHole(self):
        # Check that leftmost empty slot is taken
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=Holder)
        holder2 = Mock(_fit=None, state=State.online, spec_set=Holder)
        holder3 = Mock(_fit=None, state=State.overload, spec_set=Holder)
        holder4 = Mock(_fit=None, state=State.online, spec_set=Holder)
        fit.ordered.append(holder1)
        fit.ordered.insert(3, holder2)
        fit.ordered.insert(6, holder3)
        # Action
        fit.ordered.equip(holder4)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.ordered), 7)
        self.assertIs(fit.ordered[1], holder4)
        self.assertIs(holder4._fit, fit)
        # Misc
        fit.ordered.remove(holder1)
        fit.ordered.remove(holder2)
        fit.ordered.remove(holder3)
        fit.ordered.remove(holder4)
        self.assertObjectBuffersEmpty(fit)

    def testAttachedNoneToEmpty(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        # Action
        self.assertRaises(TypeError, fit.ordered.equip, None)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.ordered), 0)
        # Misc
        self.assertObjectBuffersEmpty(fit)

    def testAttachedHolderToEmpty(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder = Mock(_fit=None, state=State.overload, spec_set=Holder)
        # Action
        fit.ordered.equip(holder)
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
        self.assertIs(len(fit.ordered), 1)
        self.assertIs(fit.ordered[0], holder)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.ordered.remove(holder)
        self.assertObjectBuffersEmpty(fit)

    def testAttachedHolderToEmptyTypeFailure(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder = Mock(_fit=None, state=State.offline, spec_set=('_fit', 'state'))
        # Action
        self.assertRaises(TypeError, fit.ordered.equip, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.ordered), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit)

    def testAttachedHolderToEmptyValueFailure(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        fitOther = self.makeFit(eos=eos)
        holder = Mock(_fit=None, state=State.offline, spec_set=Holder)
        fitOther.ordered.equip(holder)
        # Action
        self.assertRaises(ValueError, fit.ordered.equip, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.ordered), 0)
        self.assertEqual(len(fitOther.lt), 1)
        self.assertIn(holder, fitOther.lt)
        self.assertEqual(fitOther.lt[holder], {State.offline})
        self.assertEqual(len(fitOther.rt), 1)
        self.assertIn(holder, fitOther.rt)
        self.assertEqual(fitOther.rt[holder], {State.offline})
        self.assertEqual(len(fitOther.st), 1)
        self.assertIn(holder, fitOther.st)
        self.assertEqual(fitOther.st[holder], {State.offline})
        self.assertIs(len(fitOther.ordered), 1)
        self.assertIs(fitOther.ordered[0], holder)
        self.assertIs(holder._fit, fitOther)
        # Misc
        fitOther.ordered.remove(holder)
        self.assertObjectBuffersEmpty(fit)

    def testAttachedHolderSolid(self):
        # Check case when all slots of list are filled
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.active, spec_set=Holder)
        holder2 = Mock(_fit=None, state=State.offline, spec_set=Holder)
        holder3 = Mock(_fit=None, state=State.overload, spec_set=Holder)
        fit.ordered.append(holder1)
        fit.ordered.append(holder2)
        # Action
        fit.ordered.equip(holder3)
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
        self.assertIs(len(fit.ordered), 3)
        self.assertIs(fit.ordered[2], holder3)
        self.assertIs(holder3._fit, fit)
        # Misc
        fit.ordered.remove(holder1)
        fit.ordered.remove(holder2)
        fit.ordered.remove(holder3)
        self.assertObjectBuffersEmpty(fit)

    def testAttachedHolderFirstHole(self):
        # Check that leftmost empty slot is taken
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.active, spec_set=Holder)
        holder2 = Mock(_fit=None, state=State.offline, spec_set=Holder)
        holder3 = Mock(_fit=None, state=State.online, spec_set=Holder)
        holder4 = Mock(_fit=None, state=State.active, spec_set=Holder)
        fit.ordered.append(holder1)
        fit.ordered.insert(3, holder2)
        fit.ordered.insert(6, holder3)
        # Action
        fit.ordered.equip(holder4)
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
        self.assertIs(len(fit.ordered), 7)
        self.assertIs(fit.ordered[1], holder4)
        self.assertIs(holder4._fit, fit)
        # Misc
        fit.ordered.remove(holder1)
        fit.ordered.remove(holder2)
        fit.ordered.remove(holder3)
        fit.ordered.remove(holder4)
        self.assertObjectBuffersEmpty(fit)
