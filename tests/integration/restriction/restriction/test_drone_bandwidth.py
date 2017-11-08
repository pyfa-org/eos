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
from eos.const.eos import ModifierDomain, ModifierOperator, ModifierTargetFilter
from eos.const.eve import AttributeId, EffectCategoryId
from tests.integration.restriction.restriction_testcase import (
    RestrictionTestCase)


class TestDroneBandwidth(RestrictionTestCase):
    """Check functionality of drone bandwidth restriction."""

    def setUp(self):
        RestrictionTestCase.setUp(self)
        self.ch.attr(attribute_id=AttributeId.drone_bandwidth)
        self.ch.attr(attribute_id=AttributeId.drone_bandwidth_used)

    def test_fail_excess_single(self):
        # When ship provides drone bandwidth output, but single consumer demands
        # for more, error should be raised
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.drone_bandwidth: 40}).id)
        item = Drone(
            self.ch.type(attributes={AttributeId.drone_bandwidth_used: 50}).id,
            state=State.online)
        self.fit.drones.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 40)
        self.assertEqual(restriction_error.total_use, 50)
        self.assertEqual(restriction_error.item_use, 50)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_excess_single_undefined_output(self):
        # When stats module does not specify output, make sure it's assumed to
        # be 0
        item = Drone(
            self.ch.type(attributes={AttributeId.drone_bandwidth_used: 5}).id,
            state=State.online)
        self.fit.drones.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 0)
        self.assertEqual(restriction_error.total_use, 5)
        self.assertEqual(restriction_error.item_use, 5)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_excess_multiple(self):
        # When multiple consumers require less than drone bandwidth output
        # alone, but in sum want more than total output, it should be erroneous
        # situation
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.drone_bandwidth: 40}).id)
        item1 = Drone(
            self.ch.type(attributes={AttributeId.drone_bandwidth_used: 25}).id,
            state=State.online)
        self.fit.drones.add(item1)
        item2 = Drone(
            self.ch.type(attributes={AttributeId.drone_bandwidth_used: 20}).id,
            state=State.online)
        self.fit.drones.add(item2)
        # Action
        restriction_error1 = self.get_restriction_error(
            item1, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.output, 40)
        self.assertEqual(restriction_error1.total_use, 45)
        self.assertEqual(restriction_error1.item_use, 25)
        # Action
        restriction_error2 = self.get_restriction_error(
            item2, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.output, 40)
        self.assertEqual(restriction_error2.total_use, 45)
        self.assertEqual(restriction_error2.item_use, 20)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_excess_modified(self):
        # Make sure modified drone bandwidth values are taken
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.drone_bandwidth: 50}).id)
        src_attr = self.ch.attr()
        modifier = self.mod(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr_id=AttributeId.drone_bandwidth_used,
            operator=ModifierOperator.post_mul,
            src_attr_id=src_attr.id)
        effect = self.ch.effect(
            category_id=EffectCategoryId.passive, modifiers=[modifier])
        item = Drone(
            self.ch.type(
                attributes={
                    AttributeId.drone_bandwidth_used: 50, src_attr.id: 2},
                effects=[effect]).id,
            state=State.online)
        self.fit.drones.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 50)
        self.assertEqual(restriction_error.total_use, 100)
        self.assertEqual(restriction_error.item_use, 100)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_mix_usage_zero(self):
        # If some item has zero usage and drone bandwidth error is still raised,
        # check it's not raised for item with zero usage
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.drone_bandwidth: 50}).id)
        item1 = Drone(
            self.ch.type(attributes={AttributeId.drone_bandwidth_used: 100}).id,
            state=State.online)
        self.fit.drones.add(item1)
        item2 = Drone(
            self.ch.type(attributes={AttributeId.drone_bandwidth_used: 0}).id,
            state=State.online)
        self.fit.drones.add(item2)
        # Action
        restriction_error1 = self.get_restriction_error(
            item1, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.output, 50)
        self.assertEqual(restriction_error1.total_use, 100)
        self.assertEqual(restriction_error1.item_use, 100)
        # Action
        restriction_error2 = self.get_restriction_error(
            item2, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass(self):
        # When total consumption is less than output, no errors should be raised
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.drone_bandwidth: 50}).id)
        item1 = Drone(
            self.ch.type(attributes={AttributeId.drone_bandwidth_used: 25}).id,
            state=State.online)
        self.fit.drones.add(item1)
        item2 = Drone(
            self.ch.type(attributes={AttributeId.drone_bandwidth_used: 20}).id,
            state=State.online)
        self.fit.drones.add(item2)
        # Action
        restriction_error1 = self.get_restriction_error(
            item1, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            item2, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_state(self):
        # When item isn't online, it shouldn't consume anything
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.drone_bandwidth: 40}).id)
        item = Drone(
            self.ch.type(attributes={AttributeId.drone_bandwidth_used: 50}).id,
            state=State.offline)
        self.fit.drones.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_no_source(self):
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.drone_bandwidth: 40}).id)
        item = Drone(
            self.ch.type(attributes={AttributeId.drone_bandwidth_used: 50}).id,
            state=State.online)
        self.fit.drones.add(item)
        self.fit.source = None
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
