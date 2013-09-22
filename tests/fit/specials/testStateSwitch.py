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
from eos.fit.holder.container import HolderSet
from eos.tests.fit.fitTestCase import FitTestCase


class TestHolderStateSwitch(FitTestCase):

    def makeFit(self, *args, **kwargs):
        fit = super().makeFit(*args, **kwargs)
        fit.unordered = HolderSet(fit)
        return fit

    def customMembershipCheck(self, fit, holder):
        self.assertIn(holder, fit.unordered)

    def testDetachedUpwards(self):
        fit = self.makeFit()
        # Action
        holder = Holder(1, State.offline)
        fit.unordered.add(holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        # Action
        holder.state = State.online
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        # Action
        holder.state = State.overload
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        # Misc
        fit.unordered.remove(holder)
        self.assertObjectBuffersEmpty(fit)

    def testDetachedDownwards(self):
        fit = self.makeFit()
        # Action
        holder = Holder(1, State.overload)
        fit.unordered.add(holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        # Action
        holder.state = State.active
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        # Action
        holder.state = State.offline
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        # Misc
        fit.unordered.remove(holder)
        self.assertObjectBuffersEmpty(fit)

    def testAttachedUpwards(self):
        eos = Mock(spec_set=())
        fit = self.makeFit(eos=eos)
        # Action
        holder = Holder(1, State.overload)
        fit.unordered.add(holder)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder, fit.lt)
        self.assertEqual(fit.lt[holder], {State.offline, State.online, State.active, State.overload})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder, fit.rt)
        self.assertEqual(fit.rt[holder], {State.offline, State.online, State.active, State.overload})
        # Action
        holder.state = State.active
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder, fit.lt)
        self.assertEqual(fit.lt[holder], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder, fit.rt)
        self.assertEqual(fit.rt[holder], {State.offline, State.online, State.active})
        # Action
        holder.state = State.offline
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder, fit.lt)
        self.assertEqual(fit.lt[holder], {State.offline})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder, fit.rt)
        self.assertEqual(fit.rt[holder], {State.offline})
        # Misc
        fit.unordered.remove(holder)
        self.assertObjectBuffersEmpty(fit)
