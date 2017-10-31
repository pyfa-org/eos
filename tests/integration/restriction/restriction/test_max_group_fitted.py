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
from eos.const.eve import AttributeId
from tests.integration.restriction.restriction_testcase import (
    RestrictionTestCase)


class TestMaxGroupFitted(RestrictionTestCase):
    """Check functionality of max group fitted restriction."""

    def test_fail_excess_all(self):
        # Make sure error is raised for all items exceeding their group
        # restriction
        eve_type = self.ch.type(
            group_id=6, attributes={AttributeId.max_group_fitted: 1})
        item1 = ModuleHigh(eve_type.id)
        self.fit.modules.high.append(item1)
        item2 = ModuleHigh(eve_type.id)
        self.fit.modules.high.append(item2)
        # Action
        restriction_error1 = self.get_restriction_error(
            item1, Restriction.max_group_fitted)
        # Verification
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.max_group, 1)
        self.assertEqual(restriction_error1.item_group, 6)
        self.assertEqual(restriction_error1.group_items, 2)
        # Action
        restriction_error2 = self.get_restriction_error(
            item2, Restriction.max_group_fitted)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.max_group, 1)
        self.assertEqual(restriction_error2.item_group, 6)
        self.assertEqual(restriction_error2.group_items, 2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_mix_excess_one(self):
        # Make sure error is raised for just items which excess restriction,
        # even if both are from the same group
        item1 = ModuleHigh(self.ch.type(
            group_id=92, attributes={AttributeId.max_group_fitted: 1}).id)
        self.fit.modules.high.append(item1)
        item2 = ModuleHigh(self.ch.type(
            group_id=92, attributes={AttributeId.max_group_fitted: 2}).id)
        self.fit.modules.high.append(item2)
        # Action
        restriction_error1 = self.get_restriction_error(
            item1, Restriction.max_group_fitted)
        # Verification
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.max_group, 1)
        self.assertEqual(restriction_error1.item_group, 92)
        self.assertEqual(restriction_error1.group_items, 2)
        # Action
        restriction_error2 = self.get_restriction_error(
            item2, Restriction.max_group_fitted)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass(self):
        # Make sure no errors are raised when number of added items doesn't
        # exceed any restrictions
        eve_type = self.ch.type(
            group_id=860, attributes={AttributeId.max_group_fitted: 2})
        item1 = ModuleHigh(eve_type.id)
        self.fit.modules.high.append(item1)
        item2 = ModuleHigh(eve_type.id)
        self.fit.modules.high.append(item2)
        # Action
        restriction_error1 = self.get_restriction_error(
            item1, Restriction.max_group_fitted)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            item2, Restriction.max_group_fitted)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_item_none_group(self):
        # Check that items with None group are not affected
        eve_type = self.ch.type(
            group_id=None, attributes={AttributeId.max_group_fitted: 1})
        item1 = ModuleHigh(eve_type.id)
        self.fit.modules.high.append(item1)
        item2 = ModuleHigh(eve_type.id)
        self.fit.modules.high.append(item2)
        # Action
        restriction_error1 = self.get_restriction_error(
            item1, Restriction.max_group_fitted)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            item2, Restriction.max_group_fitted)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_item_other_class(self):
        eve_type = self.ch.type(
            group_id=12, attributes={AttributeId.max_group_fitted: 1})
        item1 = Drone(eve_type.id)
        self.fit.drones.add(item1)
        item2 = Drone(eve_type.id)
        self.fit.drones.add(item2)
        # Action
        restriction_error1 = self.get_restriction_error(
            item1, Restriction.max_group_fitted)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            item2, Restriction.max_group_fitted)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_no_source(self):
        # Make sure error is raised for all items exceeding their group
        # restriction
        eve_type = self.ch.type(
            group_id=6, attributes={AttributeId.max_group_fitted: 1})
        item1 = ModuleHigh(eve_type.id)
        self.fit.modules.high.append(item1)
        item2 = ModuleHigh(eve_type.id)
        self.fit.modules.high.append(item2)
        self.fit.source = None
        # Action
        restriction_error1 = self.get_restriction_error(
            item1, Restriction.max_group_fitted)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            item2, Restriction.max_group_fitted)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
