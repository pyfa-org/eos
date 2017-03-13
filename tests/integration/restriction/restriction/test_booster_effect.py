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
from eos.const.eos import Restriction
from tests.integration.restriction.restriction_testcase import RestrictionTestCase


class TestBoosterEffect(RestrictionTestCase):
    """Check functionality of booster's hidden effects restriction"""

    def test_fail(self):
        # Check if error is raised when there's disabled effect
        fit = Fit()
        eve_type = self.ch.type()
        item = Booster(eve_type.id)
        item.side_effects = {55, 66}
        item._disabled_effects = {77, 99}
        fit.boosters.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.booster_effect)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.illegally_disabled, {77, 99})
        self.assertEqual(restriction_error.disablable, {55, 66})
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_disabled_side_effect(self):
        fit = Fit()
        eve_type = self.ch.type()
        item = Booster(eve_type.id)
        item.side_effects = {55, 66}
        item._disabled_effects = {55, 66}
        fit.boosters.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.booster_effect)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_enabled_regular_effect(self):
        fit = Fit()
        eve_type = self.ch.type()
        item = Booster(eve_type.id)
        # Enabled regular effects are not listed in any of
        # these containers
        item.side_effects = {}
        item._disabled_effects = set()
        fit.boosters.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.booster_effect)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_non_booster(self):
        fit = Fit()
        eve_type = self.ch.type()
        item = Implant(eve_type.id, strict_spec=False)
        item.side_effects = {55, 66}
        item._disabled_effects = {77, 99}
        fit.implants.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.booster_effect)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
