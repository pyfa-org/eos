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
from eos.fit.holder.item import Booster, Implant
from eos.tests.fit.fitTestCase import FitTestCase


class TestContainerOrderedPlace(FitTestCase):

    def makeFit(self, *args, **kwargs):
        fit = super().makeFit(*args, **kwargs)
        fit.container = HolderList(fit, Implant)
        return fit

    def customMembershipCheck(self, fit, holder):
        self.assertIn(holder, fit.container)

    def testDetachedHolderOutside(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.active, spec_set=Implant)
        fit.container.append(holder1)
        # Action
        fit.container.place(3, holder2)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 4)
        self.assertIs(fit.container[0], holder1)
        self.assertIsNone(fit.container[1])
        self.assertIsNone(fit.container[2])
        self.assertIs(fit.container[3], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        self.assertObjectBuffersEmpty(fit.container)

    def testDetachedNoneOutside(self):
        fit = self.makeFit()
        holder = Mock(_fit=None, state=State.active, spec_set=Implant)
        fit.container.append(holder)
        # Action
        self.assertRaises(TypeError, fit.container.place, 3, None)
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

    def testDetachedHolderOntoNone(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.overload, spec_set=Implant)
        holder3 = Mock(_fit=None, state=State.overload, spec_set=Implant)
        fit.container.append(holder1)
        fit.container.insert(3, holder2)
        # Action
        fit.container.place(1, holder3)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 4)
        self.assertIs(fit.container[0], holder1)
        self.assertIs(fit.container[1], holder3)
        self.assertIsNone(fit.container[2])
        self.assertIs(fit.container[3], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        self.assertIs(holder3._fit, fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        fit.container.remove(holder3)
        self.assertObjectBuffersEmpty(fit.container)

    def testDetachedNoneOntoNone(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.offline, spec_set=Implant)
        fit.container.append(holder1)
        fit.container.insert(3, holder2)
        # Action
        self.assertRaises(TypeError, fit.container.place, 1, None)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 4)
        self.assertIs(fit.container[0], holder1)
        self.assertIsNone(fit.container[1])
        self.assertIsNone(fit.container[2])
        self.assertIs(fit.container[3], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        self.assertObjectBuffersEmpty(fit.container)

    def testDetachedHolderOntoHolder(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.overload, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.active, spec_set=Implant)
        fit.container.append(holder1)
        # Action
        self.assertRaises(SlotTakenError, fit.container.place, 0, holder2)
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
        self.assertObjectBuffersEmpty(fit.container)

    def testDetachedNoneOntoHolder(self):
        fit = self.makeFit()
        holder = Mock(_fit=None, state=State.offline, spec_set=Implant)
        fit.container.append(holder)
        # Action
        self.assertRaises(TypeError, fit.container.place, 0, None)
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

    def testDetachedHolderOutsideTypeFailure(self):
        fit = self.makeFit()
        holder = Mock(_fit=None, state=State.overload, spec_set=Booster)
        # Action
        self.assertRaises(TypeError, fit.container.place, 2, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit.container)

    def testDetachedHolderOutsideValueFailure(self):
        fit = self.makeFit()
        fitOther = self.makeFit()
        holder = Mock(_fit=None, state=State.overload, spec_set=Implant)
        fitOther.container.append(holder)
        # Action
        self.assertRaises(ValueError, fit.container.place, 2, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fitOther.lt), 0)
        self.assertEqual(len(fitOther.rt), 0)
        self.assertEqual(len(fitOther.st), 0)
        self.assertIs(len(fit.container), 0)
        self.assertIs(len(fitOther.container), 1)
        self.assertIs(fitOther.container[0], holder)
        self.assertIs(holder._fit, fitOther)
        # Misc
        fitOther.container.remove(holder)
        self.assertObjectBuffersEmpty(fit.container)
        self.assertObjectBuffersEmpty(fitOther.container)

    def testDetachedHolderOntoNoneTypeFailure(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.online, spec_set=Booster)
        fit.container.insert(1, holder1)
        # Action
        self.assertRaises(TypeError, fit.container.place, 0, holder2)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 2)
        self.assertIsNone(fit.container[0])
        self.assertIs(fit.container[1], holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        # Misc
        fit.container.remove(holder1)
        self.assertObjectBuffersEmpty(fit.container)

    def testDetachedHolderOntoNoneValueFailure(self):
        fit = self.makeFit()
        fitOther = self.makeFit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.online, spec_set=Implant)
        fit.container.insert(1, holder1)
        fitOther.container.append(holder2)
        # Action
        self.assertRaises(ValueError, fit.container.place, 0, holder2)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fitOther.lt), 0)
        self.assertEqual(len(fitOther.rt), 0)
        self.assertEqual(len(fitOther.st), 0)
        self.assertIs(len(fit.container), 2)
        self.assertIsNone(fit.container[0])
        self.assertIs(fit.container[1], holder1)
        self.assertIs(len(fitOther.container), 1)
        self.assertIs(fitOther.container[0], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fitOther)
        # Misc
        fit.container.remove(holder1)
        fitOther.container.remove(holder2)
        self.assertObjectBuffersEmpty(fit.container)
        self.assertObjectBuffersEmpty(fitOther.container)

    def testAttachedHolderOutside(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.overload, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.offline, spec_set=Implant)
        fit.container.append(holder1)
        # Action
        fit.container.place(3, holder2)
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
        self.assertEqual(len(fit.st), 2)
        self.assertIn(holder1, fit.st)
        self.assertEqual(fit.st[holder1], {State.offline, State.online, State.active, State.overload})
        self.assertIn(holder2, fit.st)
        self.assertEqual(fit.st[holder2], {State.offline})
        self.assertIs(len(fit.container), 4)
        self.assertIs(fit.container[0], holder1)
        self.assertIsNone(fit.container[1])
        self.assertIsNone(fit.container[2])
        self.assertIs(fit.container[3], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        self.assertObjectBuffersEmpty(fit.container)

    def testAttachedNoneOutside(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder = Mock(_fit=None, state=State.active, spec_set=Implant)
        fit.container.append(holder)
        # Action
        self.assertRaises(TypeError, fit.container.place, 3, None)
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

    def testAttachedHolderOntoNone(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.active, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.online, spec_set=Implant)
        holder3 = Mock(_fit=None, state=State.online, spec_set=Implant)
        fit.container.append(holder1)
        fit.container.insert(3, holder2)
        # Action
        fit.container.place(1, holder3)
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
        self.assertEqual(len(fit.st), 3)
        self.assertIn(holder1, fit.st)
        self.assertEqual(fit.st[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder2, fit.st)
        self.assertEqual(fit.st[holder2], {State.offline, State.online})
        self.assertIn(holder3, fit.st)
        self.assertEqual(fit.st[holder3], {State.offline, State.online})
        self.assertIs(len(fit.container), 4)
        self.assertIs(fit.container[0], holder1)
        self.assertIs(fit.container[1], holder3)
        self.assertIsNone(fit.container[2])
        self.assertIs(fit.container[3], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        self.assertIs(holder3._fit, fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        fit.container.remove(holder3)
        self.assertObjectBuffersEmpty(fit.container)

    def testAttachedNoneOntoNone(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.offline, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.offline, spec_set=Implant)
        fit.container.append(holder1)
        fit.container.insert(3, holder2)
        # Action
        self.assertRaises(TypeError, fit.container.place, 1, None)
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
        self.assertEqual(len(fit.st), 2)
        self.assertIn(holder1, fit.st)
        self.assertEqual(fit.st[holder1], {State.offline})
        self.assertIn(holder2, fit.st)
        self.assertEqual(fit.st[holder2], {State.offline})
        self.assertIs(len(fit.container), 4)
        self.assertIs(fit.container[0], holder1)
        self.assertIsNone(fit.container[1])
        self.assertIsNone(fit.container[2])
        self.assertIs(fit.container[3], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        self.assertObjectBuffersEmpty(fit.container)

    def testAttachedHolderOntoHolder(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.active, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.overload, spec_set=Implant)
        fit.container.append(holder1)
        # Action
        self.assertRaises(SlotTakenError, fit.container.place, 0, holder2)
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
        self.assertObjectBuffersEmpty(fit.container)

    def testAttachedNoneOntoHolder(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder = Mock(_fit=None, state=State.active, spec_set=Implant)
        fit.container.append(holder)
        # Action
        self.assertRaises(TypeError, fit.container.place, 0, None)
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

    def testAttachedHolderOutsideTypeFailure(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder = Mock(_fit=None, state=State.online, spec_set=Booster)
        # Action
        self.assertRaises(TypeError, fit.container.place, 2, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit.container)

    def testAttachedHolderOutsideValueFailure(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        fitOther = self.makeFit(eos=eos)
        holder = Mock(_fit=None, state=State.online, spec_set=Implant)
        fitOther.container.append(holder)
        # Action
        self.assertRaises(ValueError, fit.container.place, 2, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fitOther.lt), 1)
        self.assertIn(holder, fitOther.lt)
        self.assertEqual(fitOther.lt[holder], {State.offline, State.online})
        self.assertEqual(len(fitOther.rt), 1)
        self.assertIn(holder, fitOther.rt)
        self.assertEqual(fitOther.rt[holder], {State.offline, State.online})
        self.assertEqual(len(fitOther.st), 1)
        self.assertIn(holder, fitOther.st)
        self.assertEqual(fitOther.st[holder], {State.offline, State.online})
        self.assertIs(len(fit.container), 0)
        self.assertIs(len(fitOther.container), 1)
        self.assertIs(fitOther.container[0], holder)
        self.assertIs(holder._fit, fitOther)
        # Misc
        fitOther.container.remove(holder)
        self.assertObjectBuffersEmpty(fit.container)
        self.assertObjectBuffersEmpty(fitOther.container)

    def testAttachedHolderOntoNoneTypeFailure(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.offline, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.active, spec_set=Booster)
        fit.container.insert(1, holder1)
        # Action
        self.assertRaises(TypeError, fit.container.place, 0, holder2)
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
        self.assertIs(len(fit.container), 2)
        self.assertIsNone(fit.container[0])
        self.assertIs(fit.container[1], holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        # Misc
        fit.container.remove(holder1)
        self.assertObjectBuffersEmpty(fit.container)

    def testAttachedHolderOntoNoneValueFailure(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        fitOther = self.makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.offline, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.active, spec_set=Implant)
        fit.container.insert(1, holder1)
        fitOther.container.append(holder2)
        # Action
        self.assertRaises(ValueError, fit.container.place, 0, holder2)
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
        self.assertEqual(len(fitOther.lt), 1)
        self.assertIn(holder2, fitOther.lt)
        self.assertEqual(fitOther.lt[holder2], {State.offline, State.online, State.active})
        self.assertEqual(len(fitOther.rt), 1)
        self.assertIn(holder2, fitOther.rt)
        self.assertEqual(fitOther.rt[holder2], {State.offline, State.online, State.active})
        self.assertEqual(len(fitOther.st), 1)
        self.assertIn(holder2, fitOther.st)
        self.assertEqual(fitOther.st[holder2], {State.offline, State.online, State.active})
        self.assertIs(len(fit.container), 2)
        self.assertIsNone(fit.container[0])
        self.assertIs(fit.container[1], holder1)
        self.assertIs(len(fitOther.container), 1)
        self.assertIs(fitOther.container[0], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fitOther)
        # Misc
        fit.container.remove(holder1)
        fitOther.container.remove(holder2)
        self.assertObjectBuffersEmpty(fit.container)
        self.assertObjectBuffersEmpty(fitOther.container)
