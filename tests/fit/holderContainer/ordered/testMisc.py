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
from eos.fit.holder.item import Implant
from eos.tests.fit.fitTestCase import FitTestCase


class TestContainerOrderedMisc(FitTestCase):

    def makeFit(self, *args, **kwargs):
        fit = super().makeFit(*args, **kwargs)
        fit.container = HolderList(fit, Implant)
        return fit

    def customMembershipCheck(self, fit, holder):
        self.assertIn(holder, fit.container)

    def testLen(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.overload, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.offline, spec_set=Implant)
        self.assertEqual(len(fit.container), 0)
        fit.container.append(holder1)
        self.assertEqual(len(fit.container), 1)
        fit.container.place(3, holder2)
        self.assertEqual(len(fit.container), 4)
        fit.container.remove(holder1)
        self.assertEqual(len(fit.container), 3)
        fit.container.remove(holder2)
        self.assertEqual(len(fit.container), 0)
        self.assertObjectBuffersEmpty(fit.container)

    def testContains(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.offline, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.offline, spec_set=Implant)
        self.assertFalse(holder1 in fit.container)
        self.assertFalse(None in fit.container)
        self.assertFalse(holder2 in fit.container)
        fit.container.append(holder1)
        self.assertTrue(holder1 in fit.container)
        self.assertFalse(None in fit.container)
        self.assertFalse(holder2 in fit.container)
        fit.container.place(3, holder2)
        self.assertTrue(holder1 in fit.container)
        self.assertTrue(None in fit.container)
        self.assertTrue(holder2 in fit.container)
        fit.container.remove(holder1)
        self.assertFalse(holder1 in fit.container)
        self.assertTrue(None in fit.container)
        self.assertTrue(holder2 in fit.container)
        fit.container.remove(holder2)
        self.assertFalse(holder1 in fit.container)
        self.assertFalse(None in fit.container)
        self.assertFalse(holder2 in fit.container)
        self.assertObjectBuffersEmpty(fit.container)

    def testIter(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.active, spec_set=Implant)
        self.assertEqual(list(holder for holder in fit.container), [])
        fit.container.append(holder1)
        self.assertEqual(list(holder for holder in fit.container), [holder1])
        fit.container.place(3, holder2)
        self.assertEqual(list(holder for holder in fit.container), [holder1, None, None, holder2])
        fit.container.remove(holder1)
        self.assertEqual(list(holder for holder in fit.container), [None, None, holder2])
        fit.container.remove(holder2)
        self.assertEqual(list(holder for holder in fit.container), [])
        self.assertObjectBuffersEmpty(fit.container)

    def testDetachedClear(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.overload, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.online, spec_set=Implant)
        fit.container.append(holder1)
        fit.container.place(3, holder2)
        # Action
        fit.container.clear()
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit.container)

    def testAttachedClear(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.overload, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.overload, spec_set=Implant)
        fit.container.append(holder1)
        fit.container.place(3, holder2)
        # Action
        fit.container.clear()
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit.container)

    def testSlice(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.active, spec_set=Implant)
        fit.container.append(holder1)
        fit.container.place(3, holder2)
        sliceFull = fit.container[:]
        self.assertEqual(len(sliceFull), 4)
        self.assertIs(sliceFull[0], holder1)
        self.assertIsNone(sliceFull[1])
        self.assertIsNone(sliceFull[2])
        self.assertIs(sliceFull[3], holder2)
        slicePositive = fit.container[0:2]
        self.assertEqual(len(slicePositive), 2)
        self.assertIs(slicePositive[0], holder1)
        self.assertIsNone(slicePositive[1])
        sliceNegative = fit.container[-2:]
        self.assertEqual(len(sliceNegative), 2)
        self.assertIsNone(sliceNegative[0])
        self.assertIs(sliceNegative[1], holder2)
        sliceStep = fit.container[::2]
        self.assertEqual(len(sliceStep), 2)
        self.assertIs(sliceStep[0], holder1)
        self.assertIsNone(sliceStep[1])
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        self.assertObjectBuffersEmpty(fit.container)

    def testHolderView(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.offline, spec_set=Implant)
        view = fit.container.holders()
        self.assertEqual(len(view), 0)
        self.assertEqual(list(view), [])
        self.assertFalse(holder1 in view)
        self.assertFalse(holder2 in view)
        self.assertFalse(None in view)
        fit.container.append(holder1)
        self.assertEqual(len(view), 1)
        self.assertEqual(list(view), [holder1])
        self.assertTrue(holder1 in view)
        self.assertFalse(holder2 in view)
        self.assertFalse(None in view)
        fit.container.place(3, holder2)
        self.assertEqual(len(view), 2)
        self.assertEqual(list(view), [holder1, holder2])
        self.assertTrue(holder1 in view)
        self.assertTrue(holder2 in view)
        self.assertFalse(None in view)
        fit.container.free(holder1)
        self.assertEqual(len(view), 1)
        self.assertEqual(list(view), [holder2])
        self.assertFalse(holder1 in view)
        self.assertTrue(holder2 in view)
        self.assertFalse(None in view)
        fit.container.free(holder2)
        self.assertEqual(len(view), 0)
        self.assertEqual(list(view), [])
        self.assertFalse(holder1 in view)
        self.assertFalse(holder2 in view)
        self.assertFalse(None in view)
        self.assertObjectBuffersEmpty(fit.container)
