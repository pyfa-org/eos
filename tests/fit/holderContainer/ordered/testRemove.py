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


class TestContainerOrderedRemove(FitTestCase):

    def makeFit(self, *args, **kwargs):
        fit = super().makeFit(*args, **kwargs)
        fit.container = HolderList(fit, Implant)
        return fit

    def customMembershipCheck(self, fit, holder):
        self.assertIn(holder, fit.container)

    def testDetachedHolder(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.online, spec_set=Implant)
        fit.container.append(holder1)
        fit.container.append(holder2)
        # Action
        fit.container.remove(holder1)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], holder2)
        self.assertIsNone(holder1._fit)
        self.assertIs(holder2._fit, fit)
        # Action
        fit.container.remove(holder2)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit.container)

    def testDetachedHolderAfterNones(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.overload, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.active, spec_set=Implant)
        holder3 = Mock(_fit=None, state=State.overload, spec_set=Implant)
        fit.container.append(holder1)
        fit.container.place(3, holder2)
        fit.container.place(6, holder3)
        # Action
        fit.container.remove(holder2)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 6)
        self.assertIs(fit.container[0], holder1)
        self.assertIsNone(fit.container[1])
        self.assertIsNone(fit.container[2])
        self.assertIsNone(fit.container[3])
        self.assertIsNone(fit.container[4])
        self.assertIs(fit.container[5], holder3)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        self.assertIs(holder3._fit, fit)
        # Action
        fit.container.remove(holder3)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        self.assertIsNone(holder3._fit)
        # Misc
        fit.container.remove(holder1)
        self.assertObjectBuffersEmpty(fit.container)

    def testDetachedHolderFailure(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.offline, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.online, spec_set=Implant)
        fit.container.append(holder1)
        # Action
        self.assertRaises(ValueError, fit.container.remove, holder2)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        # Misc
        fit.container.remove(holder1)
        # Action
        self.assertRaises(ValueError, fit.container.remove, holder1)
        # checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit.container)

    def testDetachedNone(self):
        # Check that first found None is removed
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.offline, spec_set=Implant)
        fit.container.place(1, holder1)
        fit.container.place(3, holder2)
        # Action
        fit.container.remove(None)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 3)
        self.assertIs(fit.container[0], holder1)
        self.assertIsNone(fit.container[1])
        self.assertIs(fit.container[2], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        self.assertObjectBuffersEmpty(fit.container)

    def testDetachedNoneFailure(self):
        fit = self.makeFit()
        holder = Mock(_fit=None, state=State.overload, spec_set=Implant)
        fit.container.append(holder)
        # Action
        self.assertRaises(ValueError, fit.container.remove, None)
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

    def testDetachedIndexHolder(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.overload, spec_set=Implant)
        fit.container.append(holder1)
        fit.container.append(holder2)
        # Action
        fit.container.remove(0)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], holder2)
        self.assertIsNone(holder1._fit)
        self.assertIs(holder2._fit, fit)
        # Action
        fit.container.remove(0)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit.container)

    def testDetachedIndexNone(self):
        fit = self.makeFit()
        holder = Mock(_fit=None, state=State.online, spec_set=Implant)
        fit.container.place(1, holder)
        # Action
        fit.container.remove(0)
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

    def testDetachedIndexAfterNones(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.offline, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.online, spec_set=Implant)
        holder3 = Mock(_fit=None, state=State.active, spec_set=Implant)
        fit.container.append(holder1)
        fit.container.place(3, holder2)
        fit.container.place(6, holder3)
        # Action
        fit.container.remove(3)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 6)
        self.assertIs(fit.container[0], holder1)
        self.assertIsNone(fit.container[1])
        self.assertIsNone(fit.container[2])
        self.assertIsNone(fit.container[3])
        self.assertIsNone(fit.container[4])
        self.assertIs(fit.container[5], holder3)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        self.assertIs(holder3._fit, fit)
        # Action
        fit.container.remove(5)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        self.assertIsNone(holder3._fit)
        # Misc
        fit.container.remove(holder1)
        self.assertObjectBuffersEmpty(fit.container)

    def testDetachedIndexOutside(self):
        fit = self.makeFit()
        holder = Mock(_fit=None, state=State.offline, spec_set=Implant)
        fit.container.append(holder)
        # Action
        self.assertRaises(IndexError, fit.container.remove, 5)
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

    def testAttachedHolder(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.active, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.overload, spec_set=Implant)
        fit.container.append(holder1)
        fit.container.append(holder2)
        # Action
        fit.container.remove(holder1)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder2, fit.lt)
        self.assertEqual(fit.lt[holder2], {State.offline, State.online, State.active, State.overload})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder2, fit.rt)
        self.assertEqual(fit.rt[holder2], {State.offline, State.online, State.active, State.overload})
        self.assertEqual(len(fit.st), 1)
        self.assertIn(holder2, fit.st)
        self.assertEqual(fit.st[holder2], {State.offline, State.online, State.active, State.overload})
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], holder2)
        self.assertIsNone(holder1._fit)
        self.assertIs(holder2._fit, fit)
        # Action
        fit.container.remove(holder2)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit.container)

    def testAttachedHolderAfterNones(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.active, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.overload, spec_set=Implant)
        holder3 = Mock(_fit=None, state=State.offline, spec_set=Implant)
        fit.container.append(holder1)
        fit.container.place(3, holder2)
        fit.container.place(6, holder3)
        # Action
        fit.container.remove(holder2)
        # Checks
        self.assertEqual(len(fit.lt), 2)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder3, fit.lt)
        self.assertEqual(fit.lt[holder3], {State.offline})
        self.assertEqual(len(fit.rt), 2)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder3, fit.rt)
        self.assertEqual(fit.rt[holder3], {State.offline})
        self.assertEqual(len(fit.st), 2)
        self.assertIn(holder1, fit.st)
        self.assertEqual(fit.st[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder3, fit.st)
        self.assertEqual(fit.st[holder3], {State.offline})
        self.assertIs(len(fit.container), 6)
        self.assertIs(fit.container[0], holder1)
        self.assertIsNone(fit.container[1])
        self.assertIsNone(fit.container[2])
        self.assertIsNone(fit.container[3])
        self.assertIsNone(fit.container[4])
        self.assertIs(fit.container[5], holder3)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        self.assertIs(holder3._fit, fit)
        # Action
        fit.container.remove(holder3)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.st), 1)
        self.assertIn(holder1, fit.st)
        self.assertEqual(fit.st[holder1], {State.offline, State.online, State.active})
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        self.assertIsNone(holder3._fit)
        # Misc
        fit.container.remove(holder1)
        self.assertObjectBuffersEmpty(fit.container)

    def testAttachedHolderFailure(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.active, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.overload, spec_set=Implant)
        fit.container.append(holder1)
        # Action
        self.assertRaises(ValueError, fit.container.remove, holder2)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.st), 1)
        self.assertIn(holder1, fit.st)
        self.assertEqual(fit.st[holder1], {State.offline, State.online, State.active})
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        # Misc
        fit.container.remove(holder1)
        # Action
        self.assertRaises(ValueError, fit.container.remove, holder1)
        # checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit.container)

    def testAttachedNone(self):
        # Check that first found None is removed
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.offline, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.online, spec_set=Implant)
        fit.container.place(1, holder1)
        fit.container.place(3, holder2)
        # Action
        fit.container.remove(None)
        # Checks
        self.assertEqual(len(fit.lt), 2)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline})
        self.assertIn(holder2, fit.lt)
        self.assertEqual(fit.lt[holder2], {State.offline, State.online})
        self.assertEqual(len(fit.rt), 2)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline})
        self.assertIn(holder2, fit.rt)
        self.assertEqual(fit.rt[holder2], {State.offline, State.online})
        self.assertEqual(len(fit.st), 2)
        self.assertIn(holder1, fit.st)
        self.assertEqual(fit.st[holder1], {State.offline})
        self.assertIn(holder2, fit.st)
        self.assertEqual(fit.st[holder2], {State.offline, State.online})
        self.assertIs(len(fit.container), 3)
        self.assertIs(fit.container[0], holder1)
        self.assertIsNone(fit.container[1])
        self.assertIs(fit.container[2], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        self.assertObjectBuffersEmpty(fit.container)

    def testAttachedNoneFailure(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder = Mock(_fit=None, state=State.overload, spec_set=Implant)
        fit.container.append(holder)
        # Action
        self.assertRaises(ValueError, fit.container.remove, None)
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

    def testAttachedIndexHolder(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.overload, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.active, spec_set=Implant)
        fit.container.append(holder1)
        fit.container.append(holder2)
        # Action
        fit.container.remove(0)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder2, fit.lt)
        self.assertEqual(fit.lt[holder2], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder2, fit.rt)
        self.assertEqual(fit.rt[holder2], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.st), 1)
        self.assertIn(holder2, fit.st)
        self.assertEqual(fit.st[holder2], {State.offline, State.online, State.active})
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], holder2)
        self.assertIsNone(holder1._fit)
        self.assertIs(holder2._fit, fit)
        # Action
        fit.container.remove(0)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit.container)

    def testAttachedIndexNone(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder = Mock(_fit=None, state=State.active, spec_set=Implant)
        fit.container.place(1, holder)
        # Action
        fit.container.remove(0)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder, fit.lt)
        self.assertEqual(fit.lt[holder], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder, fit.rt)
        self.assertEqual(fit.rt[holder], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.st), 1)
        self.assertIn(holder, fit.st)
        self.assertEqual(fit.st[holder], {State.offline, State.online, State.active})
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], holder)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.container.remove(holder)
        self.assertObjectBuffersEmpty(fit.container)

    def testAttachedIndexAfterNones(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.active, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.offline, spec_set=Implant)
        holder3 = Mock(_fit=None, state=State.online, spec_set=Implant)
        fit.container.append(holder1)
        fit.container.place(3, holder2)
        fit.container.place(6, holder3)
        # Action
        fit.container.remove(3)
        # Checks
        self.assertEqual(len(fit.lt), 2)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder3, fit.lt)
        self.assertEqual(fit.lt[holder3], {State.offline, State.online})
        self.assertEqual(len(fit.rt), 2)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder3, fit.rt)
        self.assertEqual(fit.rt[holder3], {State.offline, State.online})
        self.assertEqual(len(fit.st), 2)
        self.assertIn(holder1, fit.st)
        self.assertEqual(fit.st[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder3, fit.st)
        self.assertEqual(fit.st[holder3], {State.offline, State.online})
        self.assertIs(len(fit.container), 6)
        self.assertIs(fit.container[0], holder1)
        self.assertIsNone(fit.container[1])
        self.assertIsNone(fit.container[2])
        self.assertIsNone(fit.container[3])
        self.assertIsNone(fit.container[4])
        self.assertIs(fit.container[5], holder3)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        self.assertIs(holder3._fit, fit)
        # Action
        fit.container.remove(5)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.st), 1)
        self.assertIn(holder1, fit.st)
        self.assertEqual(fit.st[holder1], {State.offline, State.online, State.active})
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        self.assertIsNone(holder3._fit)
        # Misc
        fit.container.remove(holder1)
        self.assertObjectBuffersEmpty(fit.container)

    def testAttachedIndexOutside(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder = Mock(_fit=None, state=State.active, spec_set=Implant)
        fit.container.append(holder)
        # Action
        self.assertRaises(IndexError, fit.container.remove, 5)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder, fit.lt)
        self.assertEqual(fit.lt[holder], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder, fit.rt)
        self.assertEqual(fit.rt[holder], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.st), 1)
        self.assertIn(holder, fit.st)
        self.assertEqual(fit.st[holder], {State.offline, State.online, State.active})
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], holder)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.container.remove(holder)
        self.assertObjectBuffersEmpty(fit.container)
