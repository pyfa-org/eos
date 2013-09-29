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


class TestContainerOrderedMisc(FitTestCase):

    def makeFit(self, *args, **kwargs):
        fit = super().makeFit(*args, **kwargs)
        fit.ordered = HolderList(fit)
        return fit

    def customMembershipCheck(self, fit, holder):
        self.assertIn(holder, fit.ordered)

    def testLen(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.overload, spec_set=Holder)
        holder2 = Mock(_fit=None, state=State.offline, spec_set=Holder)
        self.assertEqual(len(fit.ordered), 0)
        fit.ordered.append(holder1)
        self.assertEqual(len(fit.ordered), 1)
        fit.ordered.place(3, holder2)
        self.assertEqual(len(fit.ordered), 4)
        fit.ordered.remove(holder1)
        self.assertEqual(len(fit.ordered), 3)
        fit.ordered.remove(holder2)
        self.assertEqual(len(fit.ordered), 0)
        self.assertObjectBuffersEmpty(fit)

    def testContains(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.offline, spec_set=Holder)
        holder2 = Mock(_fit=None, state=State.offline, spec_set=Holder)
        self.assertFalse(holder1 in fit.ordered)
        self.assertFalse(None in fit.ordered)
        self.assertFalse(holder2 in fit.ordered)
        fit.ordered.append(holder1)
        self.assertTrue(holder1 in fit.ordered)
        self.assertFalse(None in fit.ordered)
        self.assertFalse(holder2 in fit.ordered)
        fit.ordered.place(3, holder2)
        self.assertTrue(holder1 in fit.ordered)
        self.assertTrue(None in fit.ordered)
        self.assertTrue(holder2 in fit.ordered)
        fit.ordered.remove(holder1)
        self.assertFalse(holder1 in fit.ordered)
        self.assertTrue(None in fit.ordered)
        self.assertTrue(holder2 in fit.ordered)
        fit.ordered.remove(holder2)
        self.assertFalse(holder1 in fit.ordered)
        self.assertFalse(None in fit.ordered)
        self.assertFalse(holder2 in fit.ordered)
        self.assertObjectBuffersEmpty(fit)

    def testIter(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=Holder)
        holder2 = Mock(_fit=None, state=State.active, spec_set=Holder)
        self.assertEqual(list(holder for holder in fit.ordered), [])
        fit.ordered.append(holder1)
        self.assertEqual(list(holder for holder in fit.ordered), [holder1])
        fit.ordered.place(3, holder2)
        self.assertEqual(list(holder for holder in fit.ordered), [holder1, None, None, holder2])
        fit.ordered.remove(holder1)
        self.assertEqual(list(holder for holder in fit.ordered), [None, None, holder2])
        fit.ordered.remove(holder2)
        self.assertEqual(list(holder for holder in fit.ordered), [])
        self.assertObjectBuffersEmpty(fit)

    def testDetachedClear(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.overload, spec_set=Holder)
        holder2 = Mock(_fit=None, state=State.online, spec_set=Holder)
        fit.ordered.append(holder1)
        fit.ordered.place(3, holder2)
        # Action
        fit.ordered.clear()
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.ordered), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit)

    def testAttachedClear(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.overload, spec_set=Holder)
        holder2 = Mock(_fit=None, state=State.overload, spec_set=Holder)
        fit.ordered.append(holder1)
        fit.ordered.place(3, holder2)
        # Action
        fit.ordered.clear()
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.ordered), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit)

    def testHolderView(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=Holder)
        holder2 = Mock(_fit=None, state=State.offline, spec_set=Holder)
        view = fit.ordered.holders()
        self.assertEqual(len(view), 0)
        self.assertEqual(list(view), [])
        self.assertFalse(holder1 in view)
        self.assertFalse(holder2 in view)
        self.assertFalse(None in view)
        fit.ordered.append(holder1)
        self.assertEqual(len(view), 1)
        self.assertEqual(list(view), [holder1])
        self.assertTrue(holder1 in view)
        self.assertFalse(holder2 in view)
        self.assertFalse(None in view)
        fit.ordered.place(3, holder2)
        self.assertEqual(len(view), 2)
        self.assertEqual(list(view), [holder1, holder2])
        self.assertTrue(holder1 in view)
        self.assertTrue(holder2 in view)
        self.assertFalse(None in view)
        fit.ordered.free(holder1)
        self.assertEqual(len(view), 1)
        self.assertEqual(list(view), [holder2])
        self.assertFalse(holder1 in view)
        self.assertTrue(holder2 in view)
        self.assertFalse(None in view)
        fit.ordered.free(holder2)
        self.assertEqual(len(view), 0)
        self.assertEqual(list(view), [])
        self.assertFalse(holder1 in view)
        self.assertFalse(holder2 in view)
        self.assertFalse(None in view)
        self.assertObjectBuffersEmpty(fit)
