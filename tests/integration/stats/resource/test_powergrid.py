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
from tests.integration.stats.stat_testcase import StatTestCase


class TestPowergrid(StatTestCase):

    def setUp(self):
        super().setUp()
        self.ch.attribute(attribute_id=AttributeId.power_output)
        self.ch.attribute(attribute_id=AttributeId.power)
        self.effect = self.ch.effect(
            effect_id=EffectId.online, category=EffectCategoryId.active,
            customize=True)

    def test_output(self):
        # Check that modified attribute of ship is used
        src_attr = self.ch.attribute()
        modifier = self.mod(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=AttributeId.power_output,
            operator=ModifierOperator.post_mul,
            src_attr=src_attr.id)
        mod_effect = self.ch.effect(
            category=EffectCategoryId.passive, modifiers=[modifier])
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.power_output: 200, src_attr.id: 2},
            effects=[mod_effect]).id)
        # Verification
        self.assertAlmostEqual(self.fit.stats.powergrid.output, 400)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_output_no_ship(self):
        # None for output when no ship
        # Verification
        self.assertIsNone(self.fit.stats.powergrid.output)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_output_no_attr(self):
        # None for output when no attribute on ship
        self.fit.ship = Ship(self.ch.type().id)
        # Verification
        self.assertIsNone(self.fit.stats.powergrid.output)
        # Cleanup
        # Log entry is due to inability to calculate requested attribute
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(self.fit)

    def test_use_single(self):
        # Check that modified consumption attribute is used
        src_attr = self.ch.attribute()
        modifier = self.mod(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=AttributeId.power,
            operator=ModifierOperator.post_mul,
            src_attr=src_attr.id)
        mod_effect = self.ch.effect(
            category=EffectCategoryId.passive, modifiers=[modifier])
        self.fit.modules.high.append(ModuleHigh(
            self.ch.type(
                attributes={AttributeId.power: 100, src_attr.id: 0.5},
                effects=(self.effect, mod_effect)).id,
            state=State.online))
        # Verification
        self.assertAlmostEqual(self.fit.stats.powergrid.used, 50)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_use_single_rounding(self):
        self.fit.modules.high.append(ModuleHigh(
            self.ch.type(
                attributes={AttributeId.power: 55.5555555555},
                effects=[self.effect]).id,
            state=State.online))
        # Verification
        self.assertAlmostEqual(self.fit.stats.powergrid.used, 55.56)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_use_multiple(self):
        self.fit.modules.high.append(ModuleHigh(
            self.ch.type(
                attributes={AttributeId.power: 50}, effects=[self.effect]).id,
            state=State.online))
        self.fit.modules.high.append(ModuleHigh(
            self.ch.type(
                attributes={AttributeId.power: 30}, effects=[self.effect]).id,
            state=State.online))
        # Verification
        self.assertAlmostEqual(self.fit.stats.powergrid.used, 80)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_use_state(self):
        self.fit.modules.high.append(ModuleHigh(
            self.ch.type(
                attributes={AttributeId.power: 50}, effects=[self.effect]).id,
            state=State.online))
        self.fit.modules.high.append(ModuleHigh(
            self.ch.type(
                attributes={AttributeId.power: 30}, effects=[self.effect]).id,
            state=State.offline))
        # Verification
        self.assertAlmostEqual(self.fit.stats.powergrid.used, 50)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_use_disabled_effect(self):
        item1 = ModuleHigh(
            self.ch.type(
                attributes={AttributeId.power: 50}, effects=[self.effect]).id,
            state=State.online)
        item2 = ModuleHigh(
            self.ch.type(
                attributes={AttributeId.power: 30}, effects=[self.effect]).id,
            state=State.online)
        item2.set_effect_run_mode(self.effect.id, EffectRunMode.force_stop)
        self.fit.modules.high.append(item1)
        self.fit.modules.high.append(item2)
        # Verification
        self.assertAlmostEqual(self.fit.stats.powergrid.used, 50)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_use_none(self):
        # Verification
        self.assertAlmostEqual(self.fit.stats.powergrid.used, 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_no_source(self):
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.power_output: 200}).id)
        self.fit.modules.high.append(ModuleHigh(
            self.ch.type(
                attributes={AttributeId.power: 50}, effects=[self.effect]).id,
            state=State.online))
        self.fit.modules.high.append(ModuleHigh(
            self.ch.type(
                attributes={AttributeId.power: 30}, effects=[self.effect]).id,
            state=State.online))
        self.fit.source = None
        # Verification
        self.assertAlmostEqual(self.fit.stats.powergrid.used, 0)
        self.assertIsNone(self.fit.stats.powergrid.output)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)
