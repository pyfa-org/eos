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


from eos.const.eos import Restriction, State
from eos.const.eve import Attribute
from eos.fit.item import ModuleHigh, Rig
from tests.restrictions.restriction_testcase import RestrictionTestCase


class TestMaxGroupActive(RestrictionTestCase):
    """Check functionality of max group active restriction"""

    def test_fail_excess_all(self):
        # Make sure error is raised for all items exceeding
        # their group restriction
        eve_type = self.ch.type(type_id=1, group=6, attributes={Attribute.max_group_active: 1})
        item1 = self.make_item_mock(ModuleHigh, eve_type, state=State.active)
        self.add_item(item1)
        item2 = self.make_item_mock(ModuleHigh, eve_type, state=State.active)
        self.add_item(item2)
        # Action
        restriction_error1 = self.get_restriction_error(item1, Restriction.max_group_active)
        # Verification
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.max_group, 1)
        self.assertEqual(restriction_error1.item_group, 6)
        self.assertEqual(restriction_error1.group_items, 2)
        # Action
        restriction_error2 = self.get_restriction_error(item2, Restriction.max_group_active)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.max_group, 1)
        self.assertEqual(restriction_error2.item_group, 6)
        self.assertEqual(restriction_error2.group_items, 2)
        # Cleanup
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_mix_excess_one(self):
        # Make sure error is raised for just items which excess
        # restriction, even if both are from the same group
        eve_type1 = self.ch.type(type_id=1, group=92, attributes={Attribute.max_group_active: 1})
        item1 = self.make_item_mock(ModuleHigh, eve_type1, state=State.active)
        self.add_item(item1)
        eve_type2 = self.ch.type(type_id=2, group=92, attributes={Attribute.max_group_active: 2})
        item2 = self.make_item_mock(ModuleHigh, eve_type2, state=State.active)
        self.add_item(item2)
        # Action
        restriction_error1 = self.get_restriction_error(item1, Restriction.max_group_active)
        # Verification
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.max_group, 1)
        self.assertEqual(restriction_error1.item_group, 92)
        self.assertEqual(restriction_error1.group_items, 2)
        # Action
        restriction_error2 = self.get_restriction_error(item2, Restriction.max_group_active)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_mix_excess_attr_eve_type(self):
        # Check that eve type attributes are used
        eve_type1 = self.ch.type(type_id=1, group=61, attributes={Attribute.max_group_active: 1})
        item1 = self.make_item_mock(ModuleHigh, eve_type1, state=State.active)
        item1.attributes = {Attribute.max_group_active: 2}
        self.add_item(item1)
        eve_type2 = self.ch.type(type_id=2, group=61, attributes={Attribute.max_group_active: 2})
        item2 = self.make_item_mock(ModuleHigh, eve_type2, state=State.active)
        item2.attributes = {Attribute.max_group_active: 1}
        self.add_item(item2)
        # Action
        restriction_error1 = self.get_restriction_error(item1, Restriction.max_group_active)
        # Verification
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.max_group, 1)
        self.assertEqual(restriction_error1.item_group, 61)
        self.assertEqual(restriction_error1.group_items, 2)
        # Action
        restriction_error2 = self.get_restriction_error(item2, Restriction.max_group_active)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass(self):
        # Make sure no errors are raised when number of added
        # items doesn't exceed any restrictions
        eve_type = self.ch.type(type_id=1, group=860, attributes={Attribute.max_group_active: 2})
        item1 = self.make_item_mock(ModuleHigh, eve_type, state=State.active)
        self.add_item(item1)
        item2 = self.make_item_mock(ModuleHigh, eve_type, state=State.active)
        self.add_item(item2)
        # Action
        restriction_error1 = self.get_restriction_error(item1, Restriction.max_group_active)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(item2, Restriction.max_group_active)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_item_none_group(self):
        # Check that items with None group are not affected
        eve_type = self.ch.type(type_id=1, group=None, attributes={Attribute.max_group_active: 1})
        item1 = self.make_item_mock(ModuleHigh, eve_type, state=State.active)
        self.add_item(item1)
        item2 = self.make_item_mock(ModuleHigh, eve_type, state=State.active)
        self.add_item(item2)
        # Action
        restriction_error1 = self.get_restriction_error(item1, Restriction.max_group_active)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(item2, Restriction.max_group_active)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_state(self):
        # No errors should occur if items are not active+
        eve_type = self.ch.type(type_id=1, group=886, attributes={Attribute.max_group_active: 1})
        item1 = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        self.add_item(item1)
        item2 = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        self.add_item(item2)
        # Action
        restriction_error1 = self.get_restriction_error(item1, Restriction.max_group_active)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(item2, Restriction.max_group_active)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_item_non_module(self):
        # Items not belonging to ship shouldn't be affected
        eve_type = self.ch.type(type_id=1, group=12, attributes={Attribute.max_group_active: 1})
        item1 = self.make_item_mock(Rig, eve_type, state=State.active)
        self.add_item(item1)
        item2 = self.make_item_mock(Rig, eve_type, state=State.active)
        self.add_item(item2)
        # Action
        restriction_error1 = self.get_restriction_error(item1, Restriction.max_group_active)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(item2, Restriction.max_group_active)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()
