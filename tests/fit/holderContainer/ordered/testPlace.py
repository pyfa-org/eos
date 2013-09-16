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
from eos.fit.holder.container import HolderList, SlotTakenError
from eos.tests.fit.fitTestCase import FitTestCase


class TestContainerOrderedPlace(FitTestCase):

    def _makeFit(self, *args, **kwargs):
        fit = super()._makeFit(*args, **kwargs)
        fit.ordered = HolderList(fit)
        return fit

    def _customMembershipCheck(self, fit, holder):
        self.assertIn(holder, fit.ordered)

    def testDetachedHolderOutside(self):
        fit = self._makeFit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=('_fit', 'state'))
        holder2 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fit.ordered.append(holder1)
        # Action
        fit.ordered.place(3, holder2)
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

    def testDetachedNoneOutside(self):
        fit = self._makeFit()
        holder = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fit.ordered.append(holder)
        # Action
        self.assertRaises(TypeError, fit.ordered.place, 3, None)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertIs(len(fit.ordered), 1)
        self.assertIs(fit.ordered[0], holder)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.ordered.remove(holder)
        self.assertObjectBuffersEmpty(fit)

    def testDetachedHolderOntoNone(self):
        fit = self._makeFit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        holder2 = Mock(_fit=None, state=State.overload, spec_set=('_fit', 'state'))
        holder3 = Mock(_fit=None, state=State.overload, spec_set=('_fit', 'state'))
        fit.ordered.append(holder1)
        fit.ordered.insert(3, holder2)
        # Action
        fit.ordered.place(1, holder3)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertIs(len(fit.ordered), 4)
        self.assertIs(fit.ordered[0], holder1)
        self.assertIs(fit.ordered[1], holder3)
        self.assertIsNone(fit.ordered[2])
        self.assertIs(fit.ordered[3], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        self.assertIs(holder3._fit, fit)
        # Misc
        fit.ordered.remove(holder1)
        fit.ordered.remove(holder2)
        fit.ordered.remove(holder3)
        self.assertObjectBuffersEmpty(fit)

    def testDetachedNoneOntoNone(self):
        fit = self._makeFit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=('_fit', 'state'))
        holder2 = Mock(_fit=None, state=State.offline, spec_set=('_fit', 'state'))
        fit.ordered.append(holder1)
        fit.ordered.insert(3, holder2)
        # Action
        self.assertRaises(TypeError, fit.ordered.place, 1, None)
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

    def testDetachedHolderOntoHolder(self):
        fit = self._makeFit()
        holder1 = Mock(_fit=None, state=State.overload, spec_set=('_fit', 'state'))
        holder2 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fit.ordered.append(holder1)
        # Action
        self.assertRaises(SlotTakenError, fit.ordered.place, 0, holder2)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertIs(len(fit.ordered), 1)
        self.assertIs(fit.ordered[0], holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        # Misc
        fit.ordered.remove(holder1)
        self.assertObjectBuffersEmpty(fit)

    def testDetachedNoneOntoHolder(self):
        fit = self._makeFit()
        holder = Mock(_fit=None, state=State.offline, spec_set=('_fit', 'state'))
        fit.ordered.append(holder)
        # Action
        self.assertRaises(TypeError, fit.ordered.place, 0, None)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertIs(len(fit.ordered), 1)
        self.assertIs(fit.ordered[0], holder)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.ordered.remove(holder)
        self.assertObjectBuffersEmpty(fit)

    def testDetachedHolderOutsideFailure(self):
        fit = self._makeFit()
        fitOther = self._makeFit()
        holder = Mock(_fit=None, state=State.overload, spec_set=('_fit', 'state'))
        fitOther.ordered.append(holder)
        # Action
        self.assertRaises(ValueError, fit.ordered.place, 2, holder)
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

    def testDetachedHolderOntoNoneFailure(self):
        fit = self._makeFit()
        fitOther = self._makeFit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=('_fit', 'state'))
        holder2 = Mock(_fit=None, state=State.online, spec_set=('_fit', 'state'))
        fit.ordered.insert(1, holder1)
        fitOther.ordered.append(holder2)
        # Action
        self.assertRaises(ValueError, fit.ordered.place, 0, holder2)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fitOther.lt), 0)
        self.assertEqual(len(fitOther.rt), 0)
        self.assertIs(len(fit.ordered), 2)
        self.assertIsNone(fit.ordered[0])
        self.assertIs(fit.ordered[1], holder1)
        self.assertIs(len(fitOther.ordered), 1)
        self.assertIs(fitOther.ordered[0], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fitOther)
        # Misc
        fit.ordered.remove(holder1)
        fitOther.ordered.remove(holder2)
        self.assertObjectBuffersEmpty(fit)
        self.assertObjectBuffersEmpty(fitOther)

    def testAttachedHolderOutside(self):
        eos = Mock(spec_set=())
        fit = self._makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.overload, spec_set=('_fit', 'state'))
        holder2 = Mock(_fit=None, state=State.offline, spec_set=('_fit', 'state'))
        fit.ordered.append(holder1)
        # Action
        fit.ordered.place(3, holder2)
        # Checks
        self.assertEqual(len(fit.lt), 2)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online, State.active, State.overload})
        self.assertIn(holder2, fit.lt)
        self.assertEqual(fit.lt[holder2], {State.offline})
        self.assertEqual(len(fit.rt), 2)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online, State.active, State.overload})
        self.assertIn(holder2, fit.rt)
        self.assertEqual(fit.rt[holder2], {State.offline})
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

    def testAttachedNoneOutside(self):
        eos = Mock(spec_set=())
        fit = self._makeFit(eos=eos)
        holder = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fit.ordered.append(holder)
        # Action
        self.assertRaises(TypeError, fit.ordered.place, 3, None)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder, fit.lt)
        self.assertEqual(fit.lt[holder], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder, fit.rt)
        self.assertEqual(fit.rt[holder], {State.offline, State.online, State.active})
        self.assertIs(len(fit.ordered), 1)
        self.assertIs(fit.ordered[0], holder)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.ordered.remove(holder)
        self.assertObjectBuffersEmpty(fit)

    def testAttachedHolderOntoNone(self):
        eos = Mock(spec_set=())
        fit = self._makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        holder2 = Mock(_fit=None, state=State.online, spec_set=('_fit', 'state'))
        holder3 = Mock(_fit=None, state=State.online, spec_set=('_fit', 'state'))
        fit.ordered.append(holder1)
        fit.ordered.insert(3, holder2)
        # Action
        fit.ordered.place(1, holder3)
        # Checks
        self.assertEqual(len(fit.lt), 3)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder2, fit.lt)
        self.assertEqual(fit.lt[holder2], {State.offline, State.online})
        self.assertIn(holder3, fit.lt)
        self.assertEqual(fit.lt[holder3], {State.offline, State.online})
        self.assertEqual(len(fit.rt), 3)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder2, fit.rt)
        self.assertEqual(fit.rt[holder2], {State.offline, State.online})
        self.assertIn(holder3, fit.rt)
        self.assertEqual(fit.rt[holder3], {State.offline, State.online})
        self.assertIs(len(fit.ordered), 4)
        self.assertIs(fit.ordered[0], holder1)
        self.assertIs(fit.ordered[1], holder3)
        self.assertIsNone(fit.ordered[2])
        self.assertIs(fit.ordered[3], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        self.assertIs(holder3._fit, fit)
        # Misc
        fit.ordered.remove(holder1)
        fit.ordered.remove(holder2)
        fit.ordered.remove(holder3)
        self.assertObjectBuffersEmpty(fit)

    def testAttachedNoneOntoNone(self):
        eos = Mock(spec_set=())
        fit = self._makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.offline, spec_set=('_fit', 'state'))
        holder2 = Mock(_fit=None, state=State.offline, spec_set=('_fit', 'state'))
        fit.ordered.append(holder1)
        fit.ordered.insert(3, holder2)
        # Action
        self.assertRaises(TypeError, fit.ordered.place, 1, None)
        # Checks
        self.assertEqual(len(fit.lt), 2)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline})
        self.assertIn(holder2, fit.lt)
        self.assertEqual(fit.lt[holder2], {State.offline})
        self.assertEqual(len(fit.rt), 2)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline})
        self.assertIn(holder2, fit.rt)
        self.assertEqual(fit.rt[holder2], {State.offline})
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

    def testAttachedHolderOntoHolder(self):
        eos = Mock(spec_set=())
        fit = self._makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        holder2 = Mock(_fit=None, state=State.overload, spec_set=('_fit', 'state'))
        fit.ordered.append(holder1)
        # Action
        self.assertRaises(SlotTakenError, fit.ordered.place, 0, holder2)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online, State.active})
        self.assertIs(len(fit.ordered), 1)
        self.assertIs(fit.ordered[0], holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        # Misc
        fit.ordered.remove(holder1)
        self.assertObjectBuffersEmpty(fit)

    def testAttachedNoneOntoHolder(self):
        eos = Mock(spec_set=())
        fit = self._makeFit(eos=eos)
        holder = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fit.ordered.append(holder)
        # Action
        self.assertRaises(TypeError, fit.ordered.place, 0, None)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder, fit.lt)
        self.assertEqual(fit.lt[holder], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder, fit.rt)
        self.assertEqual(fit.rt[holder], {State.offline, State.online, State.active})
        self.assertIs(len(fit.ordered), 1)
        self.assertIs(fit.ordered[0], holder)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.ordered.remove(holder)
        self.assertObjectBuffersEmpty(fit)

    def testAttachedHolderOutsideFailure(self):
        eos = Mock(spec_set=())
        fit = self._makeFit(eos=eos)
        fitOther = self._makeFit(eos=eos)
        holder = Mock(_fit=None, state=State.online, spec_set=('_fit', 'state'))
        fitOther.ordered.append(holder)
        # Action
        self.assertRaises(ValueError, fit.ordered.place, 2, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fitOther.lt), 1)
        self.assertIn(holder, fitOther.lt)
        self.assertEqual(fitOther.lt[holder], {State.offline, State.online})
        self.assertEqual(len(fitOther.rt), 1)
        self.assertIn(holder, fitOther.rt)
        self.assertEqual(fitOther.rt[holder], {State.offline, State.online})
        self.assertIs(len(fit.ordered), 0)
        self.assertIs(len(fitOther.ordered), 1)
        self.assertIs(fitOther.ordered[0], holder)
        self.assertIs(holder._fit, fitOther)
        # Misc
        fitOther.ordered.remove(holder)
        self.assertObjectBuffersEmpty(fit)
        self.assertObjectBuffersEmpty(fitOther)

    def testAttachedHolderOntoNoneFailure(self):
        eos = Mock(spec_set=())
        fit = self._makeFit(eos=eos)
        fitOther = self._makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.offline, spec_set=('_fit', 'state'))
        holder2 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fit.ordered.insert(1, holder1)
        fitOther.ordered.append(holder2)
        # Action
        self.assertRaises(ValueError, fit.ordered.place, 0, holder2)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline})
        self.assertEqual(len(fitOther.lt), 1)
        self.assertIn(holder2, fitOther.lt)
        self.assertEqual(fitOther.lt[holder2], {State.offline, State.online, State.active})
        self.assertEqual(len(fitOther.rt), 1)
        self.assertIn(holder2, fitOther.rt)
        self.assertEqual(fitOther.rt[holder2], {State.offline, State.online, State.active})
        self.assertIs(len(fit.ordered), 2)
        self.assertIsNone(fit.ordered[0])
        self.assertIs(fit.ordered[1], holder1)
        self.assertIs(len(fitOther.ordered), 1)
        self.assertIs(fitOther.ordered[0], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fitOther)
        # Misc
        fit.ordered.remove(holder1)
        fitOther.ordered.remove(holder2)
        self.assertObjectBuffersEmpty(fit)
        self.assertObjectBuffersEmpty(fitOther)
