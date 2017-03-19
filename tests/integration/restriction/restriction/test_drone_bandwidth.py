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
from eos.const.eos import ModifierTargetFilter, ModifierDomain, ModifierOperator
from eos.const.eve import Attribute, EffectCategory
from eos.data.cache_object.modifier import DogmaModifier
from tests.integration.restriction.restriction_testcase import RestrictionTestCase


class TestDroneBandwidth(RestrictionTestCase):
    """Check functionality of drone bandwidth restriction"""

    def setUp(self):
        super().setUp()
        self.ch.attribute(attribute_id=Attribute.drone_bandwidth)
        self.ch.attribute(attribute_id=Attribute.drone_bandwidth_used)

    def test_fail_excess_single(self):
        # When ship provides drone bandwidth output, but single consumer
        # demands for more, error should be raised
        fit = Fit()
        fit.ship = Ship(self.ch.type(attributes={Attribute.drone_bandwidth: 40}).id)
        item = Drone(self.ch.type(attributes={Attribute.drone_bandwidth_used: 50}).id, state=State.online)
        fit.drones.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 40)
        self.assertEqual(restriction_error.total_use, 50)
        self.assertEqual(restriction_error.item_use, 50)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_fail_excess_single_undefined_output(self):
        # When stats module does not specify output, make sure
        # it's assumed to be 0
        fit = Fit()
        item = Drone(self.ch.type(attributes={Attribute.drone_bandwidth_used: 5}).id, state=State.online)
        fit.drones.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 0)
        self.assertEqual(restriction_error.total_use, 5)
        self.assertEqual(restriction_error.item_use, 5)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_fail_excess_multiple(self):
        # When multiple consumers require less than drone bandwidth output
        # alone, but in sum want more than total output, it should
        # be erroneous situation
        fit = Fit()
        fit.ship = Ship(self.ch.type(attributes={Attribute.drone_bandwidth: 40}).id)
        item1 = Drone(self.ch.type(attributes={Attribute.drone_bandwidth_used: 25}).id, state=State.online)
        fit.drones.add(item1)
        item2 = Drone(self.ch.type(attributes={Attribute.drone_bandwidth_used: 20}).id, state=State.online)
        fit.drones.add(item2)
        # Action
        restriction_error1 = self.get_restriction_error(fit, item1, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.output, 40)
        self.assertEqual(restriction_error1.total_use, 45)
        self.assertEqual(restriction_error1.item_use, 25)
        # Action
        restriction_error2 = self.get_restriction_error(fit, item2, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.output, 40)
        self.assertEqual(restriction_error2.total_use, 45)
        self.assertEqual(restriction_error2.item_use, 20)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_fail_excess_modified(self):
        # Make sure modified drone bandwidth values are taken
        fit = Fit()
        fit.ship = Ship(self.ch.type(attributes={Attribute.drone_bandwidth: 50}).id)
        src_attr = self.ch.attribute()
        modifier = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=Attribute.drone_bandwidth_used,
            operator=ModifierOperator.post_mul,
            src_attr=src_attr.id
        )
        effect = self.ch.effect(category=EffectCategory.passive, modifiers=[modifier])
        item = Drone(self.ch.type(
            effects=[effect], attributes={Attribute.drone_bandwidth_used: 50, src_attr.id: 2}
        ).id, state=State.online)
        fit.drones.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 50)
        self.assertEqual(restriction_error.total_use, 100)
        self.assertEqual(restriction_error.item_use, 100)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_mix_usage_zero(self):
        # If some item has zero usage and drone bandwidth error is
        # still raised, check it's not raised for item with
        # zero usage
        fit = Fit()
        fit.ship = Ship(self.ch.type(attributes={Attribute.drone_bandwidth: 50}).id)
        item1 = Drone(self.ch.type(attributes={Attribute.drone_bandwidth_used: 100}).id, state=State.online)
        fit.drones.add(item1)
        item2 = Drone(self.ch.type(attributes={Attribute.drone_bandwidth_used: 0}).id, state=State.online)
        fit.drones.add(item2)
        # Action
        restriction_error1 = self.get_restriction_error(fit, item1, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.output, 50)
        self.assertEqual(restriction_error1.total_use, 100)
        self.assertEqual(restriction_error1.item_use, 100)
        # Action
        restriction_error2 = self.get_restriction_error(fit, item2, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass(self):
        # When total consumption is less than output,
        # no errors should be raised
        fit = Fit()
        fit.ship = Ship(self.ch.type(attributes={Attribute.drone_bandwidth: 50}).id)
        item1 = Drone(self.ch.type(attributes={Attribute.drone_bandwidth_used: 25}).id, state=State.online)
        fit.drones.add(item1)
        item2 = Drone(self.ch.type(attributes={Attribute.drone_bandwidth_used: 20}).id, state=State.online)
        fit.drones.add(item2)
        # Action
        restriction_error1 = self.get_restriction_error(fit, item1, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(fit, item2, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_state(self):
        # When item isn't online, it shouldn't consume anything
        fit = Fit()
        fit.ship = Ship(self.ch.type(attributes={Attribute.drone_bandwidth: 40}).id)
        item = Drone(self.ch.type(attributes={Attribute.drone_bandwidth_used: 50}).id, state=State.offline)
        fit.drones.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
