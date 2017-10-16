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
from eos.const.eve import AttributeId, EffectId, EffectCategoryId
from tests.integration.item.item_testcase import ItemMixinTestCase


class TestItemDamageMissile(ItemMixinTestCase):

    def setUp(self):
        super().setUp()
        self.ch.attr(attribute_id=AttributeId.capacity)
        self.ch.attr(attribute_id=AttributeId.volume)
        self.ch.attr(attribute_id=AttributeId.charge_rate)
        self.ch.attr(attribute_id=AttributeId.reload_time)
        self.ch.attr(attribute_id=AttributeId.em_damage)
        self.ch.attr(attribute_id=AttributeId.thermal_damage)
        self.ch.attr(attribute_id=AttributeId.kinetic_damage)
        self.ch.attr(attribute_id=AttributeId.explosive_damage)
        self.cycle_attr = self.ch.attr()
        self.effect_item = self.ch.effect(
            effect_id=EffectId.use_missiles, category=EffectCategoryId.active,
            duration_attribute=self.cycle_attr.id)
        self.effect_charge = self.ch.effect(
            effect_id=EffectId.bomb_launching,
            category=EffectCategoryId.passive)

    def test_nominal_volley_generic(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.capacity: 2.0, self.cycle_attr.id: 2000,
                    AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 10000},
                effects=[self.effect_item], default_effect=self.effect_item).id,
            state=State.active)
        item.charge = Charge(self.ch.type(
            attributes={
                AttributeId.volume: 0.1, AttributeId.em_damage: 5.2,
                AttributeId.thermal_damage: 6.3,
                AttributeId.kinetic_damage: 7.4,
                AttributeId.explosive_damage: 8.5},
            effects=[self.effect_charge],
            default_effect=self.effect_charge).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 5.2)
        self.assertAlmostEqual(volley.thermal, 6.3)
        self.assertAlmostEqual(volley.kinetic, 7.4)
        self.assertAlmostEqual(volley.explosive, 8.5)
        self.assertAlmostEqual(volley.total, 27.4)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_nominal_volley_multiplier(self):
        self.ch.attr(attribute_id=AttributeId.damage_multiplier)
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.capacity: 2.0, self.cycle_attr.id: 2000,
                    AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 10000,
                    AttributeId.damage_multiplier: 5.5},
                effects=[self.effect_item], default_effect=self.effect_item).id,
            state=State.active)
        item.charge = Charge(self.ch.type(
            attributes={
                AttributeId.volume: 0.1, AttributeId.em_damage: 5.2,
                AttributeId.thermal_damage: 6.3,
                AttributeId.kinetic_damage: 7.4,
                AttributeId.explosive_damage: 8.5},
            effects=[self.effect_charge],
            default_effect=self.effect_charge).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 5.2)
        self.assertAlmostEqual(volley.thermal, 6.3)
        self.assertAlmostEqual(volley.kinetic, 7.4)
        self.assertAlmostEqual(volley.explosive, 8.5)
        self.assertAlmostEqual(volley.total, 27.4)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_nominal_volley_insufficient_state(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.capacity: 2.0, self.cycle_attr.id: 2000,
                    AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 10000},
                effects=[self.effect_item], default_effect=self.effect_item).id,
            state=State.online)
        item.charge = Charge(self.ch.type(
            attributes={
                AttributeId.volume: 0.1, AttributeId.em_damage: 5.2,
                AttributeId.thermal_damage: 6.3,
                AttributeId.kinetic_damage: 7.4,
                AttributeId.explosive_damage: 8.5},
            effects=[self.effect_charge],
            default_effect=self.effect_charge).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertIsNone(volley.total)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_nominal_volley_disabled_item_effect(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.capacity: 2.0, self.cycle_attr.id: 2000,
                    AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 10000},
                effects=[self.effect_item], default_effect=self.effect_item).id,
            state=State.active)
        item.set_effect_run_mode(self.effect_item.id, EffectRunMode.force_stop)
        item.charge = Charge(self.ch.type(
            attributes={
                AttributeId.volume: 0.1, AttributeId.em_damage: 5.2,
                AttributeId.thermal_damage: 6.3,
                AttributeId.kinetic_damage: 7.4,
                AttributeId.explosive_damage: 8.5},
            effects=[self.effect_charge],
            default_effect=self.effect_charge).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertIsNone(volley.total)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_nominal_volley_disabled_charge_effect(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.capacity: 2.0, self.cycle_attr.id: 2000,
                    AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 10000},
                effects=[self.effect_item], default_effect=self.effect_item).id,
            state=State.active)
        item.charge = Charge(self.ch.type(
            attributes={
                AttributeId.volume: 0.1, AttributeId.em_damage: 5.2,
                AttributeId.thermal_damage: 6.3,
                AttributeId.kinetic_damage: 7.4,
                AttributeId.explosive_damage: 8.5},
            effects=[self.effect_charge],
            default_effect=self.effect_charge).id)
        item.charge.set_effect_run_mode(
            self.effect_charge.id, EffectRunMode.force_stop)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertIsNone(volley.total)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_nominal_volley_no_charge(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.capacity: 2.0, self.cycle_attr.id: 2000,
                    AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 10000},
                effects=[self.effect_item], default_effect=self.effect_item).id,
            state=State.active)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertIsNone(volley.total)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_nominal_dps_no_reload(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.capacity: 2.0, self.cycle_attr.id: 2000,
                    AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 10000},
                effects=[self.effect_item], default_effect=self.effect_item).id,
            state=State.active)
        item.charge = Charge(self.ch.type(
            attributes={
                AttributeId.volume: 0.1, AttributeId.em_damage: 5.2,
                AttributeId.thermal_damage: 6.3,
                AttributeId.kinetic_damage: 7.4,
                AttributeId.explosive_damage: 8.5},
            effects=[self.effect_charge],
            default_effect=self.effect_charge).id)
        fit.modules.high.append(item)
        # Verification
        dps = item.get_nominal_dps(reload=False)
        self.assertAlmostEqual(dps.em, 2.6)
        self.assertAlmostEqual(dps.thermal, 3.15)
        self.assertAlmostEqual(dps.kinetic, 3.7)
        self.assertAlmostEqual(dps.explosive, 4.25)
        self.assertAlmostEqual(dps.total, 13.7)
        # Cleanup
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_nominal_dps_reload(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.capacity: 2.0, self.cycle_attr.id: 2000,
                    AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 10000},
                effects=[self.effect_item], default_effect=self.effect_item).id,
            state=State.active)
        item.charge = Charge(self.ch.type(
            attributes={
                AttributeId.volume: 0.1, AttributeId.em_damage: 5.2,
                AttributeId.thermal_damage: 6.3,
                AttributeId.kinetic_damage: 7.4,
                AttributeId.explosive_damage: 8.5},
            effects=[self.effect_charge],
            default_effect=self.effect_charge).id)
        fit.modules.high.append(item)
        # Verification
        dps = item.get_nominal_dps(reload=True)
        self.assertAlmostEqual(dps.em, 2.08)
        self.assertAlmostEqual(dps.thermal, 2.52)
        self.assertAlmostEqual(dps.kinetic, 2.96)
        self.assertAlmostEqual(dps.explosive, 3.4)
        self.assertAlmostEqual(dps.total, 10.96)
        # Cleanup
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)
