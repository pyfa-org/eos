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
from eos.tests.fit.fitTestCase import FitTestCase


class TestContainerOrderedFree(FitTestCase):

    def _makeFit(self, *args, **kwargs):
        fit = super()._makeFit(*args, **kwargs)
        fit.ordered = HolderList(fit)
        return fit

    def _customMembershipCheck(self, fit, holder):
        self.assertIn(holder, fit.ordered)

    def testDetachedNone(self):
        fit = self._makeFit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        holder2 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fit.ordered.append(holder1)
        fit.ordered.append(holder2)
        # Action
        self.assertRaises(ValueError, fit.ordered.free, None)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertIs(len(fit.ordered), 2)
        self.assertIs(fit.ordered[0], holder1)
        self.assertIs(fit.ordered[1], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.ordered.free(holder1)
        # Action
        fit.ordered.free(None)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertIs(len(fit.ordered), 2)
        self.assertIsNone(fit.ordered[0])
        self.assertIs(fit.ordered[1], holder2)
        self.assertIsNone(holder1._fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.ordered.free(holder2)
        self.assertObjectBuffersEmpty(fit)

    def testDetachedHolder(self):
        fit = self._makeFit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        holder2 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fit.ordered.append(holder1)
        fit.ordered.append(holder2)
        # Action
        fit.ordered.free(holder1)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertIs(len(fit.ordered), 2)
        self.assertIsNone(fit.ordered[0])
        self.assertIs(fit.ordered[1], holder2)
        self.assertIsNone(holder1._fit)
        self.assertIs(holder2._fit, fit)
        # Action
        fit.ordered.free(holder2)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertIs(len(fit.ordered), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit)

    def testDetachedHolderFailure(self):
        fit = self._makeFit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        holder2 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fit.ordered.append(holder1)
        # Action
        self.assertRaises(ValueError, fit.ordered.free, holder2)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.ordered), 1)
        self.assertIs(fit.ordered[0], holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        # Misc
        fit.ordered.free(holder1)
        # Action
        self.assertRaises(ValueError, fit.ordered.free, holder1)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.ordered), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit)

    def testDetachedHolderAfterNones(self):
        fit = self._makeFit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        holder2 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        holder3 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fit.ordered.append(holder1)
        fit.ordered.place(3, holder2)
        fit.ordered.place(6, holder3)
        # Action
        fit.ordered.free(holder2)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.ordered), 7)
        self.assertIs(fit.ordered[0], holder1)
        self.assertIsNone(fit.ordered[1])
        self.assertIsNone(fit.ordered[2])
        self.assertIsNone(fit.ordered[3])
        self.assertIsNone(fit.ordered[4])
        self.assertIsNone(fit.ordered[5])
        self.assertIs(fit.ordered[6], holder3)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        self.assertIs(holder3._fit, fit)
        # Action
        fit.ordered.free(holder3)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.ordered), 1)
        self.assertIs(fit.ordered[0], holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        self.assertIsNone(holder3._fit)
        # Misc
        fit.ordered.free(holder1)
        self.assertObjectBuffersEmpty(fit)

    def testDetachedIndexHolder(self):
        fit = self._makeFit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        holder2 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fit.ordered.append(holder1)
        fit.ordered.append(holder2)
        # Action
        fit.ordered.free(0)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.ordered), 2)
        self.assertIsNone(fit.ordered[0])
        self.assertIs(fit.ordered[1], holder2)
        self.assertIsNone(holder1._fit)
        self.assertIs(holder2._fit, fit)
        # Action
        fit.ordered.free(1)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.ordered), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit)

    def testDetachedIndexNone(self):
        fit = self._makeFit()
        holder = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fit.ordered.place(1, holder)
        # Action
        fit.ordered.free(0)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.ordered), 2)
        self.assertIsNone(fit.ordered[0])
        self.assertIs(fit.ordered[1], holder)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.ordered.free(holder)
        self.assertObjectBuffersEmpty(fit)

    def testDetachedIndexAfterNones(self):
        fit = self._makeFit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        holder2 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        holder3 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fit.ordered.append(holder1)
        fit.ordered.place(3, holder2)
        fit.ordered.place(6, holder3)
        # Action
        fit.ordered.free(3)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.ordered), 7)
        self.assertIs(fit.ordered[0], holder1)
        self.assertIsNone(fit.ordered[1])
        self.assertIsNone(fit.ordered[2])
        self.assertIsNone(fit.ordered[3])
        self.assertIsNone(fit.ordered[4])
        self.assertIsNone(fit.ordered[5])
        self.assertIs(fit.ordered[6], holder3)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        self.assertIs(holder3._fit, fit)
        # Action
        fit.ordered.free(6)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.ordered), 1)
        self.assertIs(fit.ordered[0], holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        self.assertIsNone(holder3._fit)
        # Misc
        fit.ordered.free(holder1)
        self.assertObjectBuffersEmpty(fit)

    def testDetachedIndexOutside(self):
        fit = self._makeFit()
        holder = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fit.ordered.append(holder)
        # Action
        self.assertRaises(IndexError, fit.ordered.free, 5)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.ordered), 1)
        self.assertIs(fit.ordered[0], holder)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.ordered.free(holder)
        self.assertObjectBuffersEmpty(fit)

    def testAttachedNone(self):
        eos = Mock(spec_set=())
        fit = self._makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        holder2 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fit.ordered.append(holder1)
        fit.ordered.append(holder2)
        # Action
        self.assertRaises(ValueError, fit.ordered.free, None)
        # Checks
        self.assertEqual(len(fit.lt), 2)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder2, fit.lt)
        self.assertEqual(fit.lt[holder2], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 2)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder2, fit.rt)
        self.assertEqual(fit.rt[holder2], {State.offline, State.online, State.active})
        self.assertIs(len(fit.ordered), 2)
        self.assertIs(fit.ordered[0], holder1)
        self.assertIs(fit.ordered[1], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.ordered.free(holder1)
        # Action
        fit.ordered.free(None)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder2, fit.lt)
        self.assertEqual(fit.lt[holder2], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder2, fit.rt)
        self.assertEqual(fit.rt[holder2], {State.offline, State.online, State.active})
        self.assertIs(len(fit.ordered), 2)
        self.assertIsNone(fit.ordered[0])
        self.assertIs(fit.ordered[1], holder2)
        self.assertIsNone(holder1._fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.ordered.free(holder2)
        self.assertObjectBuffersEmpty(fit)

    def testAttachedHolder(self):
        eos = Mock(spec_set=())
        fit = self._makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        holder2 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fit.ordered.append(holder1)
        fit.ordered.append(holder2)
        # Action
        fit.ordered.free(holder1)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder2, fit.lt)
        self.assertEqual(fit.lt[holder2], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder2, fit.rt)
        self.assertEqual(fit.rt[holder2], {State.offline, State.online, State.active})
        self.assertIs(len(fit.ordered), 2)
        self.assertIsNone(fit.ordered[0])
        self.assertIs(fit.ordered[1], holder2)
        self.assertIsNone(holder1._fit)
        self.assertIs(holder2._fit, fit)
        # Action
        fit.ordered.free(holder2)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertIs(len(fit.ordered), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit)

    def testAttachedHolderFailure(self):
        eos = Mock(spec_set=())
        fit = self._makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        holder2 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fit.ordered.append(holder1)
        # Action
        self.assertRaises(ValueError, fit.ordered.free, holder2)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.ordered), 1)
        self.assertIs(fit.ordered[0], holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        # Misc
        fit.ordered.free(holder1)
        # Action
        self.assertRaises(ValueError, fit.ordered.free, holder1)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.ordered), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit)

    def testAttachedHolderAfterNones(self):
        eos = Mock(spec_set=())
        fit = self._makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        holder2 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        holder3 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fit.ordered.append(holder1)
        fit.ordered.place(3, holder2)
        fit.ordered.place(6, holder3)
        # Action
        fit.ordered.free(holder2)
        # Checks
        self.assertEqual(len(fit.lt), 2)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder3, fit.lt)
        self.assertEqual(fit.lt[holder3], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 2)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder3, fit.rt)
        self.assertEqual(fit.rt[holder3], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.ordered), 7)
        self.assertIs(fit.ordered[0], holder1)
        self.assertIsNone(fit.ordered[1])
        self.assertIsNone(fit.ordered[2])
        self.assertIsNone(fit.ordered[3])
        self.assertIsNone(fit.ordered[4])
        self.assertIsNone(fit.ordered[5])
        self.assertIs(fit.ordered[6], holder3)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        self.assertIs(holder3._fit, fit)
        # Action
        fit.ordered.free(holder3)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.ordered), 1)
        self.assertIs(fit.ordered[0], holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        self.assertIsNone(holder3._fit)
        # Misc
        fit.ordered.free(holder1)
        self.assertObjectBuffersEmpty(fit)

    def testAttachedIndexHolder(self):
        eos = Mock(spec_set=())
        fit = self._makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        holder2 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fit.ordered.append(holder1)
        fit.ordered.append(holder2)
        # Action
        fit.ordered.free(0)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder2, fit.lt)
        self.assertEqual(fit.lt[holder2], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder2, fit.rt)
        self.assertEqual(fit.rt[holder2], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.ordered), 2)
        self.assertIsNone(fit.ordered[0])
        self.assertIs(fit.ordered[1], holder2)
        self.assertIsNone(holder1._fit)
        self.assertIs(holder2._fit, fit)
        # Action
        fit.ordered.free(1)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.ordered), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit)

    def testAttachedIndexNone(self):
        eos = Mock(spec_set=())
        fit = self._makeFit(eos=eos)
        holder = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fit.ordered.place(1, holder)
        # Action
        fit.ordered.free(0)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder, fit.lt)
        self.assertEqual(fit.lt[holder], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder, fit.rt)
        self.assertEqual(fit.rt[holder], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.ordered), 2)
        self.assertIsNone(fit.ordered[0])
        self.assertIs(fit.ordered[1], holder)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.ordered.free(holder)
        self.assertObjectBuffersEmpty(fit)

    def testAttachedIndexAfterNones(self):
        eos = Mock(spec_set=())
        fit = self._makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        holder2 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        holder3 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fit.ordered.append(holder1)
        fit.ordered.place(3, holder2)
        fit.ordered.place(6, holder3)
        # Action
        fit.ordered.free(3)
        # Checks
        self.assertEqual(len(fit.lt), 2)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder3, fit.lt)
        self.assertEqual(fit.lt[holder3], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 2)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder3, fit.rt)
        self.assertEqual(fit.rt[holder3], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.ordered), 7)
        self.assertIs(fit.ordered[0], holder1)
        self.assertIsNone(fit.ordered[1])
        self.assertIsNone(fit.ordered[2])
        self.assertIsNone(fit.ordered[3])
        self.assertIsNone(fit.ordered[4])
        self.assertIsNone(fit.ordered[5])
        self.assertIs(fit.ordered[6], holder3)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        self.assertIs(holder3._fit, fit)
        # Action
        fit.ordered.free(6)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.ordered), 1)
        self.assertIs(fit.ordered[0], holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        self.assertIsNone(holder3._fit)
        # Misc
        fit.ordered.free(holder1)
        self.assertObjectBuffersEmpty(fit)

    def testAttachedIndexOutside(self):
        eos = Mock(spec_set=())
        fit = self._makeFit(eos=eos)
        holder = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fit.ordered.append(holder)
        # Action
        self.assertRaises(IndexError, fit.ordered.free, 5)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder, fit.lt)
        self.assertEqual(fit.lt[holder], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder, fit.rt)
        self.assertEqual(fit.rt[holder], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.ordered), 1)
        self.assertIs(fit.ordered[0], holder)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.ordered.free(holder)
        self.assertObjectBuffersEmpty(fit)
