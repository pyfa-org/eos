# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2017 Anton Vorobyov
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
# ===============================================================================


from eos import *
from eos.const.eos import Restriction, State
from tests.integration.restriction.restriction_testcase import RestrictionTestCase


class TestState(RestrictionTestCase):
    """Check functionality of item state restriction"""

    def test_state_lower(self):
        fit = Fit()
        eve_type = self.ch.type()
        eve_type.max_state = State.active
        item = ModuleHigh(eve_type.id, state=State.online)
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.state)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_state_equal(self):
        fit = Fit()
        eve_type = self.ch.type()
        eve_type.max_state = State.active
        item = ModuleHigh(eve_type.id, state=State.active)
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.state)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_state_higher(self):
        fit = Fit()
        eve_type = self.ch.type()
        eve_type.max_state = State.active
        item = ModuleHigh(eve_type.id, state=State.overload)
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.state)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.current_state, State.overload)
        self.assertCountEqual(restriction_error.allowed_states, (State.offline, State.online, State.active))
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
