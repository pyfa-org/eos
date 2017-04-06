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
from eos.const.eve import Attribute, Effect, EffectCategory
from tests.integration.item.item_testcase import ItemMixinTestCase


class TestItemMixinChargedCycles(ItemMixinTestCase):

    def setUp(self):
        super().setUp()
        self.ch.attribute(attribute_id=Attribute.capacity)
        self.ch.attribute(attribute_id=Attribute.volume)
        self.ch.attribute(attribute_id=Attribute.charge_rate)
        self.ch.attribute(attribute_id=Attribute.hp)
        self.ch.attribute(attribute_id=Attribute.crystals_get_damaged)
        self.ch.attribute(attribute_id=Attribute.crystal_volatility_chance)
        self.ch.attribute(attribute_id=Attribute.crystal_volatility_damage)

    def test_ammo_generic(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(attributes={Attribute.capacity: 100.0, Attribute.charge_rate: 2.0}).id)
        item.charge = Charge(self.ch.type(attributes={Attribute.volume: 2.0}).id)
        fit.modules.high.append(item)
        # Verification
        self.assertEqual(item.charged_cycles, 25)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_ammo_round_down(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(attributes={Attribute.capacity: 22.0, Attribute.charge_rate: 4.0}).id)
        item.charge = Charge(self.ch.type(attributes={Attribute.volume: 2.0}).id)
        fit.modules.high.append(item)
        # Verification
        self.assertEqual(item.charged_cycles, 2)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_ammo_no_quantity(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(attributes={Attribute.charge_rate: 4.0}).id)
        item.charge = Charge(self.ch.type().id)
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.charged_cycles)
        # Cleanup
        # Attempts to fetch volume and capacity cause log entries to appear
        self.assertEqual(len(self.log), 2)
        self.assert_fit_buffers_empty(fit)

    def test_laser_combat(self):
        fit = Fit()
        effect = self.ch.effect(effect_id=Effect.target_attack, category=EffectCategory.active)
        item = ModuleHigh(self.ch.type(
            attributes={Attribute.capacity: 4.0}, effects=[effect], default_effect=effect
        ).id)
        item.charge = Charge(self.ch.type(attributes={
            Attribute.volume: 2.0, Attribute.crystals_get_damaged: 1.0, Attribute.hp: 2.2,
            Attribute.crystal_volatility_chance: 0.1, Attribute.crystal_volatility_damage: 0.01
        }).id)
        fit.modules.high.append(item)
        # Verification
        self.assertEqual(item.charged_cycles, 4400)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_laser_mining(self):
        fit = Fit()
        effect = self.ch.effect(effect_id=Effect.mining_laser, category=EffectCategory.active)
        item = ModuleHigh(self.ch.type(
            attributes={Attribute.capacity: 4.0}, effects=[effect], default_effect=effect
        ).id)
        item.charge = Charge(self.ch.type(attributes={
            Attribute.volume: 2.0, Attribute.crystals_get_damaged: 1.0, Attribute.hp: 2.2,
            Attribute.crystal_volatility_chance: 0.1, Attribute.crystal_volatility_damage: 0.01
        }).id)
        fit.modules.high.append(item)
        # Verification
        self.assertEqual(item.charged_cycles, 4400)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_laser_not_damageable(self):
        fit = Fit()
        effect = self.ch.effect(effect_id=Effect.target_attack, category=EffectCategory.active)
        item = ModuleHigh(self.ch.type(
            attributes={Attribute.capacity: 4.0}, effects=[effect], default_effect=effect
        ).id)
        item.charge = Charge(self.ch.type(attributes={
            Attribute.volume: 2.0, Attribute.hp: 2.2, Attribute.crystal_volatility_chance: 0.1,
            Attribute.crystal_volatility_damage: 0.01
        }).id)
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.charged_cycles)
        # Cleanup
        # Attempt to fetch get_damaged attribute
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_laser_no_hp(self):
        fit = Fit()
        effect = self.ch.effect(effect_id=Effect.target_attack, category=EffectCategory.active)
        item = ModuleHigh(self.ch.type(
            attributes={Attribute.capacity: 4.0}, effects=[effect], default_effect=effect
        ).id)
        item.charge = Charge(self.ch.type(attributes={
            Attribute.volume: 2.0, Attribute.crystals_get_damaged: 1.0,
            Attribute.crystal_volatility_chance: 0.1, Attribute.crystal_volatility_damage: 0.01
        }).id)
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.charged_cycles)
        # Cleanup
        # Attempt to fetch hp attribute
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_laser_no_chance(self):
        fit = Fit()
        effect = self.ch.effect(effect_id=Effect.target_attack, category=EffectCategory.active)
        item = ModuleHigh(self.ch.type(
            attributes={Attribute.capacity: 4.0}, effects=[effect], default_effect=effect
        ).id)
        item.charge = Charge(self.ch.type(attributes={
            Attribute.volume: 2.0, Attribute.crystals_get_damaged: 1.0, Attribute.hp: 2.2,
            Attribute.crystal_volatility_damage: 0.01
        }).id)
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.charged_cycles)
        # Cleanup
        # Attempt to fetch chance attribute
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_laser_no_damage(self):
        fit = Fit()
        effect = self.ch.effect(effect_id=Effect.target_attack, category=EffectCategory.active)
        item = ModuleHigh(self.ch.type(
            attributes={Attribute.capacity: 4.0}, effects=[effect], default_effect=effect
        ).id)
        item.charge = Charge(self.ch.type(attributes={
            Attribute.volume: 2.0, Attribute.crystals_get_damaged: 1.0, Attribute.hp: 2.2,
            Attribute.crystal_volatility_chance: 0.1
        }).id)
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.charged_cycles)
        # Cleanup
        # Attempt to fetch damage attribute
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_no_default_effect(self):
        fit = Fit()
        effect = self.ch.effect(effect_id=Effect.target_attack, category=EffectCategory.active)
        item = ModuleHigh(self.ch.type(attributes={Attribute.capacity: 4.0}, effects=[effect]).id)
        item.charge = Charge(self.ch.type(attributes={
            Attribute.volume: 2.0, Attribute.crystals_get_damaged: 1.0, Attribute.hp: 2.2,
            Attribute.crystal_volatility_chance: 0.1, Attribute.crystal_volatility_damage: 0.01
        }).id)
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.charged_cycles)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_no_source(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(attributes={Attribute.capacity: 100.0, Attribute.charge_rate: 2.0}).id)
        item.charge = Charge(self.ch.type(attributes={Attribute.volume: 2.0}).id)
        fit.modules.high.append(item)
        fit.source = None
        # Verification
        self.assertIsNone(item.charged_cycles)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
