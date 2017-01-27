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
from eos.fit.item import Drone, Implant
from tests.restrictions.restriction_testcase import RestrictionTestCase


class TestDroneBandwidth(RestrictionTestCase):
    """Check functionality of drone bandwidth restriction"""

    def test_fail_excess_single(self):
        # When ship provides bandwidth output, but single consumer
        # demands for more, error should be raised
        eve_type = self.ch.type(type_id=1, attributes={Attribute.drone_bandwidth_used: 0})
        item = self.make_item_mock(Drone, eve_type, state=State.online)
        item.attributes = {Attribute.drone_bandwidth_used: 50}
        self.add_item(item)
        self.fit.stats.drone_bandwidth.used = 50
        self.fit.stats.drone_bandwidth.output = 40
        restriction_error = self.get_restriction_error(item, Restriction.drone_bandwidth)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 40)
        self.assertEqual(restriction_error.total_use, 50)
        self.assertEqual(restriction_error.item_use, 50)
        self.remove_item(item)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_excess_single_other_class_domain(self):
        # Make sure items of all classes are affected
        eve_type = self.ch.type(type_id=1, attributes={Attribute.drone_bandwidth_used: 0})
        item = self.make_item_mock(Implant, eve_type, state=State.online)
        item.attributes = {Attribute.drone_bandwidth_used: 50}
        self.add_item(item)
        self.fit.stats.drone_bandwidth.used = 50
        self.fit.stats.drone_bandwidth.output = 40
        restriction_error = self.get_restriction_error(item, Restriction.drone_bandwidth)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 40)
        self.assertEqual(restriction_error.total_use, 50)
        self.assertEqual(restriction_error.item_use, 50)
        self.remove_item(item)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_excess_single_undefined_output(self):
        # When stats module does not specify output, make sure
        # it's assumed to be 0
        eve_type = self.ch.type(type_id=1, attributes={Attribute.drone_bandwidth_used: 0})
        item = self.make_item_mock(Drone, eve_type, state=State.online)
        item.attributes = {Attribute.drone_bandwidth_used: 5}
        self.add_item(item)
        self.fit.stats.drone_bandwidth.used = 5
        self.fit.stats.drone_bandwidth.output = None
        restriction_error = self.get_restriction_error(item, Restriction.drone_bandwidth)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 0)
        self.assertEqual(restriction_error.total_use, 5)
        self.assertEqual(restriction_error.item_use, 5)
        self.remove_item(item)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_excess_multiple(self):
        # When multiple consumers require less than bandwidth output
        # alone, but in sum want more than total output, it should
        # be erroneous situation
        eve_type = self.ch.type(type_id=1, attributes={Attribute.drone_bandwidth_used: 0})
        item1 = self.make_item_mock(Drone, eve_type, state=State.online)
        item1.attributes = {Attribute.drone_bandwidth_used: 25}
        self.add_item(item1)
        item2 = self.make_item_mock(Drone, eve_type, state=State.online)
        item2.attributes = {Attribute.drone_bandwidth_used: 20}
        self.add_item(item2)
        self.fit.stats.drone_bandwidth.used = 45
        self.fit.stats.drone_bandwidth.output = 40
        restriction_error1 = self.get_restriction_error(item1, Restriction.drone_bandwidth)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.output, 40)
        self.assertEqual(restriction_error1.total_use, 45)
        self.assertEqual(restriction_error1.item_use, 25)
        restriction_error2 = self.get_restriction_error(item2, Restriction.drone_bandwidth)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.output, 40)
        self.assertEqual(restriction_error2.total_use, 45)
        self.assertEqual(restriction_error2.item_use, 20)
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_excess_modified(self):
        # Make sure modified bandwidth values are taken
        eve_type = self.ch.type(type_id=1, attributes={Attribute.drone_bandwidth_used: 40})
        item = self.make_item_mock(Drone, eve_type, state=State.online)
        item.attributes = {Attribute.drone_bandwidth_used: 100}
        self.add_item(item)
        self.fit.stats.drone_bandwidth.used = 100
        self.fit.stats.drone_bandwidth.output = 50
        restriction_error = self.get_restriction_error(item, Restriction.drone_bandwidth)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 50)
        self.assertEqual(restriction_error.total_use, 100)
        self.assertEqual(restriction_error.item_use, 100)
        self.remove_item(item)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_mix_usage_negative(self):
        # If some item has negative usage and bandwidth error is
        # still raised, check it's not raised for item with
        # negative usage
        eve_type = self.ch.type(type_id=1, attributes={Attribute.drone_bandwidth_used: 0})
        item1 = self.make_item_mock(Drone, eve_type, state=State.online)
        item1.attributes = {Attribute.drone_bandwidth_used: 100}
        self.add_item(item1)
        item2 = self.make_item_mock(Drone, eve_type, state=State.online)
        item2.attributes = {Attribute.drone_bandwidth_used: -10}
        self.add_item(item2)
        self.fit.stats.drone_bandwidth.used = 90
        self.fit.stats.drone_bandwidth.output = 50
        restriction_error1 = self.get_restriction_error(item1, Restriction.drone_bandwidth)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.output, 50)
        self.assertEqual(restriction_error1.total_use, 90)
        self.assertEqual(restriction_error1.item_use, 100)
        restriction_error2 = self.get_restriction_error(item2, Restriction.drone_bandwidth)
        self.assertIsNone(restriction_error2)
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_mix_usage_zero(self):
        # If some item has zero usage and bandwidth error is
        # still raised, check it's not raised for item with
        # zero usage
        eve_type = self.ch.type(type_id=1, attributes={Attribute.drone_bandwidth_used: 0})
        item1 = self.make_item_mock(Drone, eve_type, state=State.online)
        item1.attributes = {Attribute.drone_bandwidth_used: 100}
        self.add_item(item1)
        item2 = self.make_item_mock(Drone, eve_type, state=State.online)
        item2.attributes = {Attribute.drone_bandwidth_used: 0}
        self.add_item(item2)
        self.fit.stats.drone_bandwidth.used = 100
        self.fit.stats.drone_bandwidth.output = 50
        restriction_error1 = self.get_restriction_error(item1, Restriction.drone_bandwidth)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.output, 50)
        self.assertEqual(restriction_error1.total_use, 100)
        self.assertEqual(restriction_error1.item_use, 100)
        restriction_error2 = self.get_restriction_error(item2, Restriction.drone_bandwidth)
        self.assertIsNone(restriction_error2)
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass(self):
        # When total consumption is less than output,
        # no errors should be raised
        eve_type = self.ch.type(type_id=1, attributes={Attribute.drone_bandwidth_used: 0})
        item1 = self.make_item_mock(Drone, eve_type, state=State.online)
        item1.attributes = {Attribute.drone_bandwidth_used: 25}
        self.add_item(item1)
        item2 = self.make_item_mock(Drone, eve_type, state=State.online)
        item2.attributes = {Attribute.drone_bandwidth_used: 20}
        self.add_item(item2)
        self.fit.stats.drone_bandwidth.used = 45
        self.fit.stats.drone_bandwidth.output = 50
        restriction_error1 = self.get_restriction_error(item1, Restriction.drone_bandwidth)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(item2, Restriction.drone_bandwidth)
        self.assertIsNone(restriction_error2)
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_no_attr_eve_type(self):
        # When added item's eve type doesn't have attribute, item
        # shouldn't be tracked by register, and thus, no errors
        # should be raised
        eve_type = self.ch.type(type_id=1)
        item = self.make_item_mock(Drone, eve_type, state=State.online)
        item.attributes = {Attribute.drone_bandwidth_used: 100}
        self.add_item(item)
        self.fit.stats.drone_bandwidth.used = 100
        self.fit.stats.drone_bandwidth.output = 50
        restriction_error = self.get_restriction_error(item, Restriction.drone_bandwidth)
        self.assertIsNone(restriction_error)
        self.remove_item(item)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_state(self):
        # When item isn't online, it shouldn't consume anything
        eve_type = self.ch.type(type_id=1, attributes={Attribute.drone_bandwidth_used: 0})
        item = self.make_item_mock(Drone, eve_type, state=State.offline)
        item.attributes = {Attribute.drone_bandwidth_used: 50}
        self.add_item(item)
        self.fit.stats.drone_bandwidth.used = 50
        self.fit.stats.drone_bandwidth.output = 40
        restriction_error = self.get_restriction_error(item, Restriction.drone_bandwidth)
        self.assertIsNone(restriction_error)
        self.remove_item(item)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()
