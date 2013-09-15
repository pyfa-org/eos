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
from eos.fit.holder.container import HolderSet
from eos.tests.fit.fitTestCase import FitTestCase


class TestContainerUnordered(FitTestCase):

    def _makeFit(self, *args, **kwargs):
        fit = super()._makeFit(*args, **kwargs)
        fit.unordered = HolderSet(fit)
        return fit

    def _customMembershipCheck(self, fit, holder):
        self.assertIn(holder, fit.unordered)

    def testDetachedAddNone(self):
        fit = self._makeFit()
        # Action
        self.assertRaises(ValueError, fit.unordered.add, None)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        # Misc
        self.assertFitBuffersEmpty(fit)

    def testDetachedAddHolder(self):
        fit = self._makeFit()
        holder = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        # Action
        fit.unordered.add(holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.unordered), 1)
        self.assertIn(holder, fit.unordered)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.unordered.remove(holder)
        self.assertFitBuffersEmpty(fit)

    def testDetachedAddHolderFailure(self):
        fit = self._makeFit()
        fitOther = self._makeFit()
        holder = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fitOther.unordered.add(holder)
        # Action
        self.assertRaises(ValueError, fit.unordered.add, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.unordered), 0)
        self.assertEqual(len(fitOther.lt), 0)
        self.assertEqual(len(fitOther.rt), 0)
        self.assertEqual(len(fitOther.unordered), 1)
        self.assertIn(holder, fitOther.unordered)
        self.assertIs(holder._fit, fitOther)
        # Misc
        fitOther.unordered.remove(holder)
        self.assertFitBuffersEmpty(fit)
        self.assertFitBuffersEmpty(fitOther)

    def testDetachedRemoveHolder(self):
        fit = self._makeFit()
        holder = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fit.unordered.add(holder)
        # Action
        fit.unordered.remove(holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.unordered), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assertFitBuffersEmpty(fit)

    def testDetachedRemoveHolderFailure(self):
        fit = self._makeFit()
        holder = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        # Action
        self.assertRaises(KeyError, fit.unordered.remove, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.unordered), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assertFitBuffersEmpty(fit)

    def testDetachedClear(self):
        fit = self._makeFit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        holder2 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fit.unordered.add(holder1)
        fit.unordered.add(holder2)
        # Action
        fit.unordered.clear()
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.unordered), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit)

    def testAttachedAddNone(self):
        eos = Mock(spec_set=())
        fit = self._makeFit(eos=eos)
        # Action
        self.assertRaises(ValueError, fit.unordered.add, None)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        # Misc
        self.assertFitBuffersEmpty(fit)

    def testAttachedAddHolder(self):
        eos = Mock(spec_set=())
        fit = self._makeFit(eos=eos)
        holder = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        # Action
        fit.unordered.add(holder)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder, fit.lt)
        self.assertEqual(fit.lt[holder], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder, fit.rt)
        self.assertEqual(fit.rt[holder], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.unordered), 1)
        self.assertIn(holder, fit.unordered)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.unordered.remove(holder)
        self.assertFitBuffersEmpty(fit)

    def testAttachedAddHolderFailure(self):
        eos = Mock(spec_set=())
        fit = self._makeFit(eos=eos)
        fitOther = self._makeFit(eos=eos)
        holder = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fitOther.unordered.add(holder)
        # Action
        self.assertRaises(ValueError, fit.unordered.add, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.unordered), 0)
        self.assertEqual(len(fitOther.lt), 1)
        self.assertIn(holder, fitOther.lt)
        self.assertEqual(fitOther.lt[holder], {State.offline, State.online, State.active})
        self.assertEqual(len(fitOther.rt), 1)
        self.assertIn(holder, fitOther.rt)
        self.assertEqual(fitOther.rt[holder], {State.offline, State.online, State.active})
        self.assertEqual(len(fitOther.unordered), 1)
        self.assertIn(holder, fitOther.unordered)
        self.assertIs(holder._fit, fitOther)
        # Misc
        fitOther.unordered.remove(holder)
        self.assertFitBuffersEmpty(fit)
        self.assertFitBuffersEmpty(fitOther)

    def testAttachedRemoveHolder(self):
        eos = Mock(spec_set=())
        fit = self._makeFit(eos=eos)
        holder = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fit.unordered.add(holder)
        # Action
        fit.unordered.remove(holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.unordered), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assertFitBuffersEmpty(fit)

    def testAttachedRemoveHolderFailure(self):
        eos = Mock(spec_set=())
        fit = self._makeFit(eos=eos)
        holder = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        # Action
        self.assertRaises(KeyError, fit.unordered.remove, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.unordered), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assertFitBuffersEmpty(fit)

    def testAttachedClear(self):
        eos = Mock(spec_set=())
        fit = self._makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        holder2 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        fit.unordered.add(holder1)
        fit.unordered.add(holder2)
        # Action
        fit.unordered.clear()
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.unordered), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit)

    def testLen(self):
        fit = self._makeFit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        holder2 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        self.assertEqual(len(fit.unordered), 0)
        fit.unordered.add(holder1)
        self.assertEqual(len(fit.unordered), 1)
        fit.unordered.add(holder2)
        self.assertEqual(len(fit.unordered), 2)
        fit.unordered.remove(holder1)
        self.assertEqual(len(fit.unordered), 1)
        fit.unordered.remove(holder2)
        self.assertEqual(len(fit.unordered), 0)
        self.assertObjectBuffersEmpty(fit)

    def testContains(self):
        fit = self._makeFit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        holder2 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        self.assertFalse(holder1 in fit.unordered)
        self.assertFalse(holder2 in fit.unordered)
        fit.unordered.add(holder1)
        self.assertTrue(holder1 in fit.unordered)
        self.assertFalse(holder2 in fit.unordered)
        fit.unordered.add(holder2)
        self.assertTrue(holder1 in fit.unordered)
        self.assertTrue(holder2 in fit.unordered)
        fit.unordered.remove(holder1)
        self.assertFalse(holder1 in fit.unordered)
        self.assertTrue(holder2 in fit.unordered)
        fit.unordered.remove(holder2)
        self.assertFalse(holder1 in fit.unordered)
        self.assertFalse(holder2 in fit.unordered)
        self.assertObjectBuffersEmpty(fit)

    def testIter(self):
        fit = self._makeFit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        holder2 = Mock(_fit=None, state=State.active, spec_set=('_fit', 'state'))
        self.assertEqual(set(holder for holder in fit.unordered), set())
        fit.unordered.add(holder1)
        self.assertEqual(set(holder for holder in fit.unordered), {holder1})
        fit.unordered.add(holder2)
        self.assertEqual(set(holder for holder in fit.unordered), {holder1, holder2})
        fit.unordered.remove(holder1)
        self.assertEqual(set(holder for holder in fit.unordered), {holder2})
        fit.unordered.remove(holder2)
        self.assertEqual(set(holder for holder in fit.unordered), set())
        self.assertObjectBuffersEmpty(fit)
