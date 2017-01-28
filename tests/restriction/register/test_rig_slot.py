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


from eos.const.eos import Restriction
from eos.fit.item import Implant, Rig
from tests.restriction.restriction_testcase import RestrictionTestCase


class TestRigSlot(RestrictionTestCase):
    """Check functionality of rig slot amount restriction"""

    def test_fail_excess_signle(self):
        # Check that error is raised when number of used
        # slots exceeds slot amount provided by ship
        eve_type = self.ch.type(type_id=1)
        item = self.make_item_mock(Rig, eve_type)
        self.fit.rigs.add(item)
        self.add_item(item)
        self.fit.stats.rig_slots.used = 1
        self.fit.stats.rig_slots.total = 0
        restriction_error = self.get_restriction_error(item, Restriction.rig_slot)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.slots_max_allowed, 0)
        self.assertEqual(restriction_error.slots_used, 1)
        self.remove_item(item)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_excess_single_other_class(self):
        # Make sure items of all classes are affected
        eve_type = self.ch.type(type_id=1)
        item = self.make_item_mock(Implant, eve_type)
        self.fit.rigs.add(item)
        self.add_item(item)
        self.fit.stats.rig_slots.used = 1
        self.fit.stats.rig_slots.total = 0
        restriction_error = self.get_restriction_error(item, Restriction.rig_slot)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.slots_max_allowed, 0)
        self.assertEqual(restriction_error.slots_used, 1)
        self.remove_item(item)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_excess_signle_undefined_output(self):
        # When stats module does not specify total slot amount,
        # make sure it's assumed to be 0
        eve_type = self.ch.type(type_id=1)
        item = self.make_item_mock(Rig, eve_type)
        self.fit.rigs.add(item)
        self.add_item(item)
        self.fit.stats.rig_slots.used = 1
        self.fit.stats.rig_slots.total = None
        restriction_error = self.get_restriction_error(item, Restriction.rig_slot)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.slots_max_allowed, 0)
        self.assertEqual(restriction_error.slots_used, 1)
        self.remove_item(item)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_excess_multiple(self):
        # Check that error works for multiple items
        eve_type = self.ch.type(type_id=1)
        item1 = self.make_item_mock(Rig, eve_type)
        item2 = self.make_item_mock(Rig, eve_type)
        self.fit.rigs.add(item1)
        self.fit.rigs.add(item2)
        self.add_item(item1)
        self.add_item(item2)
        self.fit.stats.rig_slots.used = 2
        self.fit.stats.rig_slots.total = 1
        restriction_error1 = self.get_restriction_error(item1, Restriction.rig_slot)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.slots_max_allowed, 1)
        self.assertEqual(restriction_error1.slots_used, 2)
        restriction_error2 = self.get_restriction_error(item2, Restriction.rig_slot)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.slots_max_allowed, 1)
        self.assertEqual(restriction_error2.slots_used, 2)
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_equal(self):
        eve_type = self.ch.type(type_id=1)
        item1 = self.make_item_mock(Rig, eve_type)
        item2 = self.make_item_mock(Rig, eve_type)
        self.fit.rigs.add(item1)
        self.fit.rigs.add(item2)
        self.add_item(item1)
        self.add_item(item2)
        self.fit.stats.rig_slots.used = 2
        self.fit.stats.rig_slots.total = 2
        restriction_error1 = self.get_restriction_error(item1, Restriction.rig_slot)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(item2, Restriction.rig_slot)
        self.assertIsNone(restriction_error2)
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_greater(self):
        eve_type = self.ch.type(type_id=1)
        item1 = self.make_item_mock(Rig, eve_type)
        item2 = self.make_item_mock(Rig, eve_type)
        self.fit.rigs.add(item1)
        self.fit.rigs.add(item2)
        self.add_item(item1)
        self.add_item(item2)
        self.fit.stats.rig_slots.used = 2
        self.fit.stats.rig_slots.total = 5
        restriction_error1 = self.get_restriction_error(item1, Restriction.rig_slot)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(item2, Restriction.rig_slot)
        self.assertIsNone(restriction_error2)
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_other_container(self):
        eve_type = self.ch.type(type_id=1)
        item = self.make_item_mock(Rig, eve_type)
        self.fit.subsystems.add(item)
        self.add_item(item)
        self.fit.stats.rig_slots.used = 1
        self.fit.stats.rig_slots.total = 0
        restriction_error = self.get_restriction_error(item, Restriction.rig_slot)
        self.assertIsNone(restriction_error)
        self.remove_item(item)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()
