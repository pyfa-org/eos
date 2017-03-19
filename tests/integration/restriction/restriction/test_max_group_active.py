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
from eos.const.eve import Attribute
from tests.integration.restriction.restriction_testcase import RestrictionTestCase


class TestMaxGroupActive(RestrictionTestCase):
    """Check functionality of max group active restriction"""

    def test_fail_excess_all(self):
        # Make sure error is raised for all items exceeding
        # their group restriction
        fit = Fit()
        eve_type = self.ch.type(group=6, attributes={Attribute.max_group_active: 1})
        item1 = ModuleHigh(eve_type.id, state=State.active)
        fit.modules.high.append(item1)
        item2 = ModuleHigh(eve_type.id, state=State.active)
        fit.modules.high.append(item2)
        # Action
        restriction_error1 = self.get_restriction_error(fit, item1, Restriction.max_group_active)
        # Verification
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.max_group, 1)
        self.assertEqual(restriction_error1.item_group, 6)
        self.assertEqual(restriction_error1.group_items, 2)
        # Action
        restriction_error2 = self.get_restriction_error(fit, item2, Restriction.max_group_active)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.max_group, 1)
        self.assertEqual(restriction_error2.item_group, 6)
        self.assertEqual(restriction_error2.group_items, 2)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_mix_excess_one(self):
        # Make sure error is raised for just items which excess
        # restriction, even if both are from the same group
        fit = Fit()
        item1 = ModuleHigh(self.ch.type(group=92, attributes={Attribute.max_group_active: 1}).id, state=State.active)
        fit.modules.high.append(item1)
        item2 = ModuleHigh(self.ch.type(group=92, attributes={Attribute.max_group_active: 2}).id, state=State.active)
        fit.modules.high.append(item2)
        # Action
        restriction_error1 = self.get_restriction_error(fit, item1, Restriction.max_group_active)
        # Verification
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.max_group, 1)
        self.assertEqual(restriction_error1.item_group, 92)
        self.assertEqual(restriction_error1.group_items, 2)
        # Action
        restriction_error2 = self.get_restriction_error(fit, item2, Restriction.max_group_active)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass(self):
        # Make sure no errors are raised when number of added
        # items doesn't exceed any restrictions
        fit = Fit()
        eve_type = self.ch.type(group=860, attributes={Attribute.max_group_active: 2})
        item1 = ModuleHigh(eve_type.id, state=State.active)
        fit.modules.high.append(item1)
        item2 = ModuleHigh(eve_type.id, state=State.active)
        fit.modules.high.append(item2)
        # Action
        restriction_error1 = self.get_restriction_error(fit, item1, Restriction.max_group_active)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(fit, item2, Restriction.max_group_active)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_item_none_group(self):
        # Check that items with None group are not affected
        fit = Fit()
        eve_type = self.ch.type(group=None, attributes={Attribute.max_group_active: 1})
        item1 = ModuleHigh(eve_type.id, state=State.active)
        fit.modules.high.append(item1)
        item2 = ModuleHigh(eve_type.id, state=State.active)
        fit.modules.high.append(item2)
        # Action
        restriction_error1 = self.get_restriction_error(fit, item1, Restriction.max_group_active)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(fit, item2, Restriction.max_group_active)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_state(self):
        # No errors should occur if items are not active+
        fit = Fit()
        eve_type = self.ch.type(group=886, attributes={Attribute.max_group_active: 1})
        item1 = ModuleHigh(eve_type.id, state=State.online)
        fit.modules.high.append(item1)
        item2 = ModuleHigh(eve_type.id, state=State.online)
        fit.modules.high.append(item2)
        # Action
        restriction_error1 = self.get_restriction_error(fit, item1, Restriction.max_group_active)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(fit, item2, Restriction.max_group_active)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_item_other_class(self):
        fit = Fit()
        eve_type = self.ch.type(group=12, attributes={Attribute.max_group_active: 1})
        item1 = Drone(eve_type.id, state=State.active)
        fit.drones.add(item1)
        item2 = Drone(eve_type.id, state=State.active)
        fit.drones.add(item2)
        # Action
        restriction_error1 = self.get_restriction_error(fit, item1, Restriction.max_group_active)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(fit, item2, Restriction.max_group_active)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
