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


class TestContainerOrderedInsert(FitTestCase):

    def makeFit(self, *args, **kwargs):
        fit = super().makeFit(*args, **kwargs)
        fit.ordered = HolderList(fit)
        return fit

    def customMembershipCheck(self, fit, holder):
        self.assertIn(holder, fit.ordered)

    def testDetachedHolderToZero(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.offline, spec_set=Holder)
        holder2 = Mock(_fit=None, state=State.active, spec_set=Holder)
        holder3 = Mock(_fit=None, state=State.online, spec_set=Holder)
        fit.ordered.append(holder1)
        fit.ordered.append(holder2)
        # Action
        fit.ordered.insert(0, holder3)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertIs(len(fit.ordered), 3)
        self.assertIs(fit.ordered[0], holder3)
        self.assertIs(fit.ordered[1], holder1)
        self.assertIs(fit.ordered[2], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        self.assertIs(holder3._fit, fit)
        # Misc
        fit.ordered.remove(holder1)
        fit.ordered.remove(holder2)
        fit.ordered.remove(holder3)
        self.assertObjectBuffersEmpty(fit)

    def testDetachedHolderToEnd(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=Holder)
        holder2 = Mock(_fit=None, state=State.overload, spec_set=Holder)
        holder3 = Mock(_fit=None, state=State.active, spec_set=Holder)
        fit.ordered.append(holder1)
        fit.ordered.append(holder2)
        # Action
        fit.ordered.insert(2, holder3)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertIs(len(fit.ordered), 3)
        self.assertIs(fit.ordered[0], holder1)
        self.assertIs(fit.ordered[1], holder2)
        self.assertIs(fit.ordered[2], holder3)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        self.assertIs(holder3._fit, fit)
        # Misc
        fit.ordered.remove(holder1)
        fit.ordered.remove(holder2)
        fit.ordered.remove(holder3)
        self.assertObjectBuffersEmpty(fit)

    def testDetachedHolderOutside(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=Holder)
        holder2 = Mock(_fit=None, state=State.offline, spec_set=Holder)
        fit.ordered.append(holder1)
        # Action
        fit.ordered.insert(3, holder2)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertIs(len(fit.ordered), 4)
        self.assertIs(fit.ordered[0], holder1)
        self.assertIsNone(fit.ordered[1])
        self.assertIsNone(fit.ordered[2])
        self.assertIs(fit.ordered[3], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.ordered.remove(holder1)
        fit.ordered.remove(holder2)
        self.assertObjectBuffersEmpty(fit)

    def testDetachedHolderInsideTypeFailure(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=Holder)
        holder2 = Mock(_fit=None, state=State.overload, spec_set=Holder)
        holder3 = Mock(_fit=None, state=State.overload, spec_set=('_fit', 'state'))
        fit.ordered.append(holder1)
        fit.ordered.append(holder2)
        # Action
        self.assertRaises(TypeError, fit.ordered.insert, 1, holder3)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertIs(len(fit.ordered), 2)
        self.assertIs(fit.ordered[0], holder1)
        self.assertIs(fit.ordered[1], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        self.assertIsNone(holder3._fit)
        # Misc
        fit.ordered.remove(holder1)
        fit.ordered.remove(holder2)
        self.assertObjectBuffersEmpty(fit)

    def testDetachedHolderInsideValueFailure(self):
        fit = self.makeFit()
        fitOther = self.makeFit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=Holder)
        holder2 = Mock(_fit=None, state=State.overload, spec_set=Holder)
        holder3 = Mock(_fit=None, state=State.overload, spec_set=Holder)
        fit.ordered.append(holder1)
        fit.ordered.append(holder2)
        fitOther.ordered.append(holder3)
        # Action
        self.assertRaises(ValueError, fit.ordered.insert, 1, holder3)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fitOther.lt), 0)
        self.assertEqual(len(fitOther.rt), 0)
        self.assertIs(len(fit.ordered), 2)
        self.assertIs(fit.ordered[0], holder1)
        self.assertIs(fit.ordered[1], holder2)
        self.assertIs(len(fitOther.ordered), 1)
        self.assertIs(fitOther.ordered[0], holder3)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        self.assertIs(holder3._fit, fitOther)
        # Misc
        fit.ordered.remove(holder1)
        fit.ordered.remove(holder2)
        fitOther.ordered.remove(holder3)
        self.assertObjectBuffersEmpty(fit)
        self.assertObjectBuffersEmpty(fitOther)

    def testDetachedHolderOutsideTypeFailure(self):
        fit = self.makeFit()
        holder = Mock(_fit=None, state=State.offline, spec_set=('_fit', 'state'))
        # Action
        self.assertRaises(TypeError, fit.ordered.insert, 4, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertIs(len(fit.ordered), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit)

    def testDetachedHolderOutsideValueFailure(self):
        fit = self.makeFit()
        fitOther = self.makeFit()
        holder = Mock(_fit=None, state=State.offline, spec_set=Holder)
        fitOther.ordered.append(holder)
        # Action
        self.assertRaises(ValueError, fit.ordered.insert, 4, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fitOther.lt), 0)
        self.assertEqual(len(fitOther.rt), 0)
        self.assertIs(len(fit.ordered), 0)
        self.assertIs(len(fitOther.ordered), 1)
        self.assertIs(fitOther.ordered[0], holder)
        self.assertIs(holder._fit, fitOther)
        # Misc
        fitOther.ordered.remove(holder)
        self.assertObjectBuffersEmpty(fit)
        self.assertObjectBuffersEmpty(fitOther)

    def testDetachedNoneInside(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=Holder)
        holder2 = Mock(_fit=None, state=State.offline, spec_set=Holder)
        fit.ordered.append(holder1)
        fit.ordered.append(holder2)
        # Action
        fit.ordered.insert(1, None)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertIs(len(fit.ordered), 3)
        self.assertIs(fit.ordered[0], holder1)
        self.assertIsNone(fit.ordered[1])
        self.assertIs(fit.ordered[2], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.ordered.remove(holder1)
        fit.ordered.remove(holder2)
        self.assertObjectBuffersEmpty(fit)

    def testDetachedNoneOutside(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.overload, spec_set=Holder)
        holder2 = Mock(_fit=None, state=State.online, spec_set=Holder)
        fit.ordered.append(holder1)
        fit.ordered.append(holder2)
        # Action
        fit.ordered.insert(6, None)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertIs(len(fit.ordered), 2)
        self.assertIs(fit.ordered[0], holder1)
        self.assertIs(fit.ordered[1], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.ordered.remove(holder1)
        fit.ordered.remove(holder2)
        self.assertObjectBuffersEmpty(fit)

    def testAttachedHolderToZero(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.active, spec_set=Holder)
        holder2 = Mock(_fit=None, state=State.online, spec_set=Holder)
        holder3 = Mock(_fit=None, state=State.active, spec_set=Holder)
        fit.ordered.append(holder1)
        fit.ordered.append(holder2)
        # Action
        fit.ordered.insert(0, holder3)
        # Checks
        self.assertEqual(len(fit.lt), 3)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder2, fit.lt)
        self.assertEqual(fit.lt[holder2], {State.offline, State.online})
        self.assertIn(holder3, fit.lt)
        self.assertEqual(fit.lt[holder3], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 3)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder2, fit.rt)
        self.assertEqual(fit.rt[holder2], {State.offline, State.online})
        self.assertIn(holder3, fit.rt)
        self.assertEqual(fit.rt[holder3], {State.offline, State.online, State.active})
        self.assertIs(len(fit.ordered), 3)
        self.assertIs(fit.ordered[0], holder3)
        self.assertIs(fit.ordered[1], holder1)
        self.assertIs(fit.ordered[2], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        self.assertIs(holder3._fit, fit)
        # Misc
        fit.ordered.remove(holder1)
        fit.ordered.remove(holder2)
        fit.ordered.remove(holder3)
        self.assertObjectBuffersEmpty(fit)

    def testAttachedHolderToEnd(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.overload, spec_set=Holder)
        holder2 = Mock(_fit=None, state=State.offline, spec_set=Holder)
        holder3 = Mock(_fit=None, state=State.offline, spec_set=Holder)
        fit.ordered.append(holder1)
        fit.ordered.append(holder2)
        # Action
        fit.ordered.insert(2, holder3)
        # Checks
        self.assertEqual(len(fit.lt), 3)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online, State.active, State.overload})
        self.assertIn(holder2, fit.lt)
        self.assertEqual(fit.lt[holder2], {State.offline})
        self.assertIn(holder3, fit.lt)
        self.assertEqual(fit.lt[holder3], {State.offline})
        self.assertEqual(len(fit.rt), 3)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online, State.active, State.overload})
        self.assertIn(holder2, fit.rt)
        self.assertEqual(fit.rt[holder2], {State.offline})
        self.assertIn(holder3, fit.rt)
        self.assertEqual(fit.rt[holder3], {State.offline})
        self.assertIs(len(fit.ordered), 3)
        self.assertIs(fit.ordered[0], holder1)
        self.assertIs(fit.ordered[1], holder2)
        self.assertIs(fit.ordered[2], holder3)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        self.assertIs(holder3._fit, fit)
        # Misc
        fit.ordered.remove(holder1)
        fit.ordered.remove(holder2)
        fit.ordered.remove(holder3)
        self.assertObjectBuffersEmpty(fit)

    def testAttachedHolderOutside(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.active, spec_set=Holder)
        holder2 = Mock(_fit=None, state=State.online, spec_set=Holder)
        fit.ordered.append(holder1)
        # Action
        fit.ordered.insert(3, holder2)
        # Checks
        self.assertEqual(len(fit.lt), 2)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder2, fit.lt)
        self.assertEqual(fit.lt[holder2], {State.offline, State.online})
        self.assertEqual(len(fit.rt), 2)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder2, fit.rt)
        self.assertEqual(fit.rt[holder2], {State.offline, State.online})
        self.assertIs(len(fit.ordered), 4)
        self.assertIs(fit.ordered[0], holder1)
        self.assertIsNone(fit.ordered[1])
        self.assertIsNone(fit.ordered[2])
        self.assertIs(fit.ordered[3], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.ordered.remove(holder1)
        fit.ordered.remove(holder2)
        self.assertObjectBuffersEmpty(fit)

    def testAttachedHolderInsideTypeFailure(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.active, spec_set=Holder)
        holder2 = Mock(_fit=None, state=State.online, spec_set=Holder)
        holder3 = Mock(_fit=None, state=State.offline, spec_set=('_fit', 'state'))
        fit.ordered.append(holder1)
        fit.ordered.append(holder2)
        # Action
        self.assertRaises(TypeError, fit.ordered.insert, 1, holder3)
        # Checks
        self.assertEqual(len(fit.lt), 2)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder2, fit.lt)
        self.assertEqual(fit.lt[holder2], {State.offline, State.online})
        self.assertEqual(len(fit.rt), 2)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder2, fit.rt)
        self.assertEqual(fit.rt[holder2], {State.offline, State.online})
        self.assertIs(len(fit.ordered), 2)
        self.assertIs(fit.ordered[0], holder1)
        self.assertIs(fit.ordered[1], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        self.assertIsNone(holder3._fit)
        # Misc
        fit.ordered.remove(holder1)
        fit.ordered.remove(holder2)
        self.assertObjectBuffersEmpty(fit)

    def testAttachedHolderInsideValueFailure(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        fitOther = self.makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.active, spec_set=Holder)
        holder2 = Mock(_fit=None, state=State.online, spec_set=Holder)
        holder3 = Mock(_fit=None, state=State.offline, spec_set=Holder)
        fit.ordered.append(holder1)
        fit.ordered.append(holder2)
        fitOther.ordered.append(holder3)
        # Action
        self.assertRaises(ValueError, fit.ordered.insert, 1, holder3)
        # Checks
        self.assertEqual(len(fit.lt), 2)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder2, fit.lt)
        self.assertEqual(fit.lt[holder2], {State.offline, State.online})
        self.assertEqual(len(fit.rt), 2)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder2, fit.rt)
        self.assertEqual(fit.rt[holder2], {State.offline, State.online})
        self.assertEqual(len(fitOther.lt), 1)
        self.assertIn(holder3, fitOther.lt)
        self.assertEqual(fitOther.lt[holder3], {State.offline})
        self.assertEqual(len(fitOther.rt), 1)
        self.assertIn(holder3, fitOther.rt)
        self.assertEqual(fitOther.rt[holder3], {State.offline})
        self.assertIs(len(fit.ordered), 2)
        self.assertIs(fit.ordered[0], holder1)
        self.assertIs(fit.ordered[1], holder2)
        self.assertIs(len(fitOther.ordered), 1)
        self.assertIs(fitOther.ordered[0], holder3)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        self.assertIs(holder3._fit, fitOther)
        # Misc
        fit.ordered.remove(holder1)
        fit.ordered.remove(holder2)
        fitOther.ordered.remove(holder3)
        self.assertObjectBuffersEmpty(fit)
        self.assertObjectBuffersEmpty(fitOther)

    def testAttachedHolderOutsideTypeFailure(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        # Action
        self.assertRaises(TypeError, fit.ordered.insert, 4, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit)

    def testAttachedHolderOutsideValueFailure(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        fitOther = self.makeFit(eos=eos)
        holder = Mock(_fit=None, state=State.active, spec_set=Holder)
        fitOther.ordered.append(holder)
        # Action
        self.assertRaises(ValueError, fit.ordered.insert, 4, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fitOther.lt), 1)
        self.assertIn(holder, fitOther.lt)
        self.assertEqual(fitOther.lt[holder], {State.offline, State.online, State.active})
        self.assertEqual(len(fitOther.rt), 1)
        self.assertIn(holder, fitOther.rt)
        self.assertEqual(fitOther.rt[holder], {State.offline, State.online, State.active})
        self.assertIs(len(fit.ordered), 0)
        self.assertIs(len(fitOther.ordered), 1)
        self.assertIs(fitOther.ordered[0], holder)
        self.assertIs(holder._fit, fitOther)
        # Misc
        fitOther.ordered.remove(holder)
        self.assertObjectBuffersEmpty(fit)
        self.assertObjectBuffersEmpty(fitOther)

    def testAttachedNoneInside(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.online, spec_set=Holder)
        holder2 = Mock(_fit=None, state=State.overload, spec_set=Holder)
        fit.ordered.append(holder1)
        fit.ordered.append(holder2)
        # Action
        fit.ordered.insert(1, None)
        # Checks
        self.assertEqual(len(fit.lt), 2)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online})
        self.assertIn(holder2, fit.lt)
        self.assertEqual(fit.lt[holder2], {State.offline, State.online, State.active, State.overload})
        self.assertEqual(len(fit.rt), 2)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online})
        self.assertIn(holder2, fit.rt)
        self.assertEqual(fit.rt[holder2], {State.offline, State.online, State.active, State.overload})
        self.assertIs(len(fit.ordered), 3)
        self.assertIs(fit.ordered[0], holder1)
        self.assertIsNone(fit.ordered[1])
        self.assertIs(fit.ordered[2], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.ordered.remove(holder1)
        fit.ordered.remove(holder2)
        self.assertObjectBuffersEmpty(fit)

    def testAttachedNoneOutside(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.online, spec_set=Holder)
        holder2 = Mock(_fit=None, state=State.online, spec_set=Holder)
        fit.ordered.append(holder1)
        fit.ordered.append(holder2)
        # Action
        fit.ordered.insert(6, None)
        # Checks
        self.assertEqual(len(fit.lt), 2)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online})
        self.assertIn(holder2, fit.lt)
        self.assertEqual(fit.lt[holder2], {State.offline, State.online})
        self.assertEqual(len(fit.rt), 2)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online})
        self.assertIn(holder2, fit.rt)
        self.assertEqual(fit.rt[holder2], {State.offline, State.online})
        self.assertIs(len(fit.ordered), 2)
        self.assertIs(fit.ordered[0], holder1)
        self.assertIs(fit.ordered[1], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.ordered.remove(holder1)
        fit.ordered.remove(holder2)
        self.assertObjectBuffersEmpty(fit)
