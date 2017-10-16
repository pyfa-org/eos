# ==============================================================================
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
# ==============================================================================


from eos import *
from eos.const.eve import EffectCategoryId
from tests.integration.restriction.restriction_testcase import (
    RestrictionTestCase)


class TestState(RestrictionTestCase):
    """Check functionality of item state restriction."""

    def test_fail_state_higher(self):
        effect = self.ch.effect(category=EffectCategoryId.active)
        item = ModuleHigh(
            self.ch.type(effects=[effect], default_effect=effect).id,
            state=State.overload)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(item, Restriction.state)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.current_state, State.overload)
        self.assertCountEqual(
            restriction_error.allowed_states,
            (State.offline, State.online, State.active))
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_pass_state_lower(self):
        effect = self.ch.effect(category=EffectCategoryId.active)
        item = ModuleHigh(
            self.ch.type(effects=[effect], default_effect=effect).id,
            state=State.online)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(item, Restriction.state)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_pass_state_equal(self):
        effect = self.ch.effect(category=EffectCategoryId.active)
        item = ModuleHigh(
            self.ch.type(effects=[effect], default_effect=effect).id,
            state=State.active)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(item, Restriction.state)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_pass_no_source(self):
        effect = self.ch.effect(category=EffectCategoryId.active)
        item = ModuleHigh(
            self.ch.type(effects=[effect], default_effect=effect).id,
            state=State.overload)
        self.fit.modules.high.append(item)
        self.fit.source = None
        # Action
        restriction_error = self.get_restriction_error(item, Restriction.state)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)
