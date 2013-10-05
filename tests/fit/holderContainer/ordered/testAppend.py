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


class TestContainerOrderedAppend(FitTestCase):

    def makeFit(self, *args, **kwargs):
        fit = super().makeFit(*args, **kwargs)
        fit.container = HolderList(fit, Implant)
        return fit

    def customMembershipCheck(self, fit, holder):
        self.assertIn(holder, fit.container)

    def testDetachedNone(self):
        fit = self.makeFit()
        # Action
        self.assertRaises(TypeError, fit.container.append, None)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        # Misc
        self.assertObjectBuffersEmpty(fit.container)

    def testDetachedHolder(self):
        fit = self.makeFit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.offline, spec_set=Implant)
        # Action
        fit.container.append(holder1)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        # Action
        fit.container.append(holder2)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 2)
        self.assertIs(fit.container[0], holder1)
        self.assertIs(fit.container[1], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        self.assertObjectBuffersEmpty(fit.container)

    def testDetachedHolderTypeFailure(self):
        fit = self.makeFit()
        holder = Mock(_fit=None, state=State.overload, spec_set=Booster)
        # Action
        self.assertRaises(TypeError, fit.container.append, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit.container)

    def testDetachedHolderValueFailure(self):
        fit = self.makeFit()
        fitOther = self.makeFit()
        holder = Mock(_fit=None, state=State.overload, spec_set=Implant)
        fitOther.container.append(holder)
        # Action
        self.assertRaises(ValueError, fit.container.append, holder)
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
        self.assertObjectBuffersEmpty(fitOther.container)

    def testAttachedNone(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        # Action
        self.assertRaises(TypeError, fit.container.append, None)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        # Misc
        self.assertObjectBuffersEmpty(fit.container)

    def testAttachedHolder(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder1 = Mock(_fit=None, state=State.online, spec_set=Implant)
        holder2 = Mock(_fit=None, state=State.active, spec_set=Implant)
        # Action
        fit.container.append(holder1)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online})
        self.assertEqual(len(fit.st), 1)
        self.assertIn(holder1, fit.st)
        self.assertEqual(fit.st[holder1], {State.offline, State.online})
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        # Action
        fit.container.append(holder2)
        # Checks
        self.assertEqual(len(fit.lt), 2)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online})
        self.assertIn(holder2, fit.lt)
        self.assertEqual(fit.lt[holder2], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 2)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online})
        self.assertIn(holder2, fit.rt)
        self.assertEqual(fit.rt[holder2], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.st), 2)
        self.assertIn(holder1, fit.st)
        self.assertEqual(fit.st[holder1], {State.offline, State.online})
        self.assertIn(holder2, fit.st)
        self.assertEqual(fit.st[holder2], {State.offline, State.online, State.active})
        self.assertIs(len(fit.container), 2)
        self.assertIs(fit.container[0], holder1)
        self.assertIs(fit.container[1], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        self.assertObjectBuffersEmpty(fit.container)

    def testAttachedHolderTypeFailure(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        holder = Mock(_fit=None, state=State.overload, spec_set=Booster)
        # Action
        self.assertRaises(TypeError, fit.container.append, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assertObjectBuffersEmpty(fit.container)

    def testAttachedHolderValueFailure(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        fitOther = self.makeFit(eos=eos)
        holder = Mock(_fit=None, state=State.overload, spec_set=Implant)
        fitOther.container.append(holder)
        # Action
        self.assertRaises(ValueError, fit.container.append, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        self.assertEqual(len(fitOther.lt), 1)
        self.assertIn(holder, fitOther.lt)
        self.assertEqual(fitOther.lt[holder], {State.offline, State.online, State.active, State.overload})
        self.assertEqual(len(fitOther.rt), 1)
        self.assertIn(holder, fitOther.rt)
        self.assertEqual(fitOther.rt[holder], {State.offline, State.online, State.active, State.overload})
        self.assertEqual(len(fitOther.st), 1)
        self.assertIn(holder, fitOther.st)
        self.assertEqual(fitOther.st[holder], {State.offline, State.online, State.active, State.overload})
        self.assertIs(len(fitOther.container), 1)
        self.assertIs(fitOther.container[0], holder)
        self.assertIs(holder._fit, fitOther)
        # Misc
        fitOther.container.remove(holder)
        self.assertObjectBuffersEmpty(fit.container)
        self.assertObjectBuffersEmpty(fitOther.container)
