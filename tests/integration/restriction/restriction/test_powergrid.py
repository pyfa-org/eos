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


class TestPowerGrid(RestrictionTestCase):
    """Check functionality of power grid restriction."""

    def setUp(self):
        super().setUp()
        self.ch.attr(attribute_id=AttributeId.power)
        self.ch.attr(attribute_id=AttributeId.power_output)
        self.effect = self.ch.effect(
            effect_id=EffectId.online, category_id=EffectCategoryId.online)

    def test_fail_excess_single(self):
        # When ship provides powergrid output, but single consumer demands for
        # more, error should be raised
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.power_output: 40}).id)
        item = ModuleHigh(
            self.ch.type(
                attributes={AttributeId.power: 50}, effects=[self.effect]).id,
            state=State.online)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.powergrid)
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
        item = ModuleHigh(
            self.ch.type(
                attributes={AttributeId.power: 5}, effects=[self.effect]).id,
            state=State.online)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.powergrid)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 0)
        self.assertEqual(restriction_error.total_use, 5)
        self.assertEqual(restriction_error.item_use, 5)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_excess_multiple(self):
        # When multiple consumers require less than powergrid output alone, but
        # in sum want more than total output, it should be erroneous situation
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.power_output: 40}).id)
        item1 = ModuleHigh(
            self.ch.type(
                attributes={AttributeId.power: 25}, effects=[self.effect]).id,
            state=State.online)
        self.fit.modules.high.append(item1)
        item2 = ModuleHigh(
            self.ch.type(
                attributes={AttributeId.power: 20}, effects=[self.effect]).id,
            state=State.online)
        self.fit.modules.high.append(item2)
        # Action
        restriction_error1 = self.get_restriction_error(
            item1, Restriction.powergrid)
        # Verification
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.output, 40)
        self.assertEqual(restriction_error1.total_use, 45)
        self.assertEqual(restriction_error1.item_use, 25)
        # Action
        restriction_error2 = self.get_restriction_error(
            item2, Restriction.powergrid)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.output, 40)
        self.assertEqual(restriction_error2.total_use, 45)
        self.assertEqual(restriction_error2.item_use, 20)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_excess_modified(self):
        # Make sure modified powergrid values are taken
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.power_output: 50}).id)
        src_attr = self.ch.attr()
        modifier = self.mod(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr_id=AttributeId.power,
            operator=ModifierOperator.post_mul,
            src_attr_id=src_attr.id)
        mod_effect = self.ch.effect(
            category_id=EffectCategoryId.passive, modifiers=[modifier])
        item = ModuleHigh(
            self.ch.type(
                attributes={AttributeId.power: 50, src_attr.id: 2},
                effects=(self.effect, mod_effect)).id,
            state=State.online)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.powergrid)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 50)
        self.assertEqual(restriction_error.total_use, 100)
        self.assertEqual(restriction_error.item_use, 100)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_mix_usage_zero(self):
        # If some item has zero usage and powergrid error is still raised, check
        # it's not raised for item with zero usage
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.power_output: 50}).id)
        item1 = ModuleHigh(
            self.ch.type(
                attributes={AttributeId.power: 100}, effects=[self.effect]).id,
            state=State.online)
        self.fit.modules.high.append(item1)
        item2 = ModuleHigh(
            self.ch.type(
                attributes={AttributeId.power: 0}, effects=[self.effect]).id,
            state=State.online)
        self.fit.modules.high.append(item2)
        # Action
        restriction_error1 = self.get_restriction_error(
            item1, Restriction.powergrid)
        # Verification
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.output, 50)
        self.assertEqual(restriction_error1.total_use, 100)
        self.assertEqual(restriction_error1.item_use, 100)
        # Action
        restriction_error2 = self.get_restriction_error(
            item2, Restriction.powergrid)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass(self):
        # When total consumption is less than output, no errors should be raised
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.power_output: 50}).id)
        item1 = ModuleHigh(
            self.ch.type(
                attributes={AttributeId.power: 25}, effects=[self.effect]).id,
            state=State.online)
        self.fit.modules.high.append(item1)
        item2 = ModuleHigh(
            self.ch.type(
                attributes={AttributeId.power: 20}, effects=[self.effect]).id,
            state=State.online)
        self.fit.modules.high.append(item2)
        # Action
        restriction_error1 = self.get_restriction_error(
            item1, Restriction.powergrid)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            item2, Restriction.powergrid)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_state(self):
        # When item isn't online, it shouldn't consume anything
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.power_output: 40}).id)
        item = ModuleHigh(
            self.ch.type(
                attributes={AttributeId.power: 50}, effects=[self.effect]).id,
            state=State.offline)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.powergrid)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_disabled_effect(self):
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.power_output: 40}).id)
        item = ModuleHigh(
            self.ch.type(
                attributes={AttributeId.power: 50}, effects=[self.effect]).id,
            state=State.online)
        item.set_effect_mode(self.effect.id, EffectMode.force_stop)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.powergrid)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_no_source(self):
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.power_output: 40}).id)
        item = ModuleHigh(
            self.ch.type(
                attributes={AttributeId.power: 50}, effects=[self.effect]).id,
            state=State.online)
        self.fit.modules.high.append(item)
        self.fit.source = None
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.powergrid)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
