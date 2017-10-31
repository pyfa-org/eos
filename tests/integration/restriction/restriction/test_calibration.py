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
from eos.const.eve import AttributeId, EffectId, EffectCategoryId
from tests.integration.restriction.restriction_testcase import (
    RestrictionTestCase)


class TestCalibration(RestrictionTestCase):
    """Check functionality of calibration restriction."""

    def setUp(self):
        super().setUp()
        self.ch.attr(attribute_id=AttributeId.upgrade_cost)
        self.ch.attr(attribute_id=AttributeId.upgrade_capacity)
        self.effect = self.ch.effect(
            effect_id=EffectId.rig_slot, category_id=EffectCategoryId.passive)

    def test_fail_excess_single(self):
        # When ship provides calibration output, but single consumer demands for
        # more, error should be raised
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.upgrade_capacity: 40}).id)
        item = Rig(self.ch.type(
            attributes={AttributeId.upgrade_cost: 50},
            effects=[self.effect]).id)
        self.fit.rigs.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.calibration)
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
        item = Rig(self.ch.type(
            attributes={AttributeId.upgrade_cost: 5},
            effects=[self.effect]).id)
        self.fit.rigs.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.calibration)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 0)
        self.assertEqual(restriction_error.total_use, 5)
        self.assertEqual(restriction_error.item_use, 5)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_excess_multiple(self):
        # When multiple consumers require less than calibration output alone,
        # but in sum want more than total output, it should be erroneous
        # situation
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.upgrade_capacity: 40}).id)
        item1 = Rig(self.ch.type(
            attributes={AttributeId.upgrade_cost: 25},
            effects=[self.effect]).id)
        self.fit.rigs.add(item1)
        item2 = Rig(self.ch.type(
            attributes={AttributeId.upgrade_cost: 20},
            effects=[self.effect]).id)
        self.fit.rigs.add(item2)
        # Action
        restriction_error1 = self.get_restriction_error(
            item1, Restriction.calibration)
        # Verification
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.output, 40)
        self.assertEqual(restriction_error1.total_use, 45)
        self.assertEqual(restriction_error1.item_use, 25)
        # Action
        restriction_error2 = self.get_restriction_error(
            item2, Restriction.calibration)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.output, 40)
        self.assertEqual(restriction_error2.total_use, 45)
        self.assertEqual(restriction_error2.item_use, 20)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_excess_modified(self):
        # Make sure modified calibration values are taken
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.upgrade_capacity: 50}).id)
        src_attr = self.ch.attr()
        modifier = self.mod(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr_id=AttributeId.upgrade_cost,
            operator=ModifierOperator.post_mul,
            src_attr_id=src_attr.id)
        mod_effect = self.ch.effect(
            category_id=EffectCategoryId.passive, modifiers=[modifier])
        item = Rig(self.ch.type(
            attributes={AttributeId.upgrade_cost: 50, src_attr.id: 2},
            effects=(self.effect, mod_effect)).id)
        self.fit.rigs.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.calibration)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 50)
        self.assertEqual(restriction_error.total_use, 100)
        self.assertEqual(restriction_error.item_use, 100)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_mix_usage_zero(self):
        # If some item has zero usage and calibration error is still raised,
        # check it's not raised for item with zero usage
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.upgrade_capacity: 50}).id)
        item1 = Rig(self.ch.type(
            attributes={AttributeId.upgrade_cost: 100},
            effects=[self.effect]).id)
        self.fit.rigs.add(item1)
        item2 = Rig(self.ch.type(
            attributes={AttributeId.upgrade_cost: 0},
            effects=[self.effect]).id)
        self.fit.rigs.add(item2)
        # Action
        restriction_error1 = self.get_restriction_error(
            item1, Restriction.calibration)
        # Verification
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.output, 50)
        self.assertEqual(restriction_error1.total_use, 100)
        self.assertEqual(restriction_error1.item_use, 100)
        # Action
        restriction_error2 = self.get_restriction_error(
            item2, Restriction.calibration)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass(self):
        # When total consumption is less than output, no errors should be raised
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.upgrade_capacity: 50}).id)
        item1 = Rig(self.ch.type(
            attributes={AttributeId.upgrade_cost: 25},
            effects=[self.effect]).id)
        self.fit.rigs.add(item1)
        item2 = Rig(self.ch.type(
            attributes={AttributeId.upgrade_cost: 20},
            effects=[self.effect]).id)
        self.fit.rigs.add(item2)
        # Action
        restriction_error1 = self.get_restriction_error(
            item1, Restriction.calibration)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            item2, Restriction.calibration)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_disabled_effect(self):
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.upgrade_capacity: 40}).id)
        item = Rig(self.ch.type(
            attributes={AttributeId.upgrade_cost: 50},
            effects=[self.effect]).id)
        item.set_effect_mode(self.effect.id, EffectMode.force_stop)
        self.fit.rigs.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.calibration)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_no_source(self):
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.upgrade_capacity: 40}).id)
        item = Rig(self.ch.type(
            attributes={AttributeId.upgrade_cost: 50},
            effects=[self.effect]).id)
        self.fit.rigs.add(item)
        self.fit.source = None
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.calibration)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
