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


from eos import Charge
from eos import Fit
from eos import ModuleHigh
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from eos.const.eve import EffectId
from tests.integration.item.testcase import ItemMixinTestCase


class TestItemMixinChargedCycles(ItemMixinTestCase):

    def setUp(self):
        ItemMixinTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.capacity)
        self.mkattr(attr_id=AttrId.volume)
        self.mkattr(attr_id=AttrId.charge_rate)
        self.mkattr(attr_id=AttrId.hp)
        self.mkattr(attr_id=AttrId.crystals_get_damaged)
        self.mkattr(attr_id=AttrId.crystal_volatility_chance)
        self.mkattr(attr_id=AttrId.crystal_volatility_dmg)

    def test_ammo_generic(self):
        fit = Fit()
        item = ModuleHigh(self.mktype(attrs={
            AttrId.capacity: 100.0,
            AttrId.charge_rate: 2.0}).id)
        item.charge = Charge(self.mktype(attrs={AttrId.volume: 2.0}).id)
        fit.modules.high.append(item)
        # Verification
        self.assertEqual(item.charged_cycles, 25)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_ammo_round_down(self):
        fit = Fit()
        item = ModuleHigh(self.mktype(attrs={
            AttrId.capacity: 22.0,
            AttrId.charge_rate: 4.0}).id)
        item.charge = Charge(self.mktype(attrs={AttrId.volume: 2.0}).id)
        fit.modules.high.append(item)
        # Verification
        self.assertEqual(item.charged_cycles, 2)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_ammo_no_quantity(self):
        fit = Fit()
        item = ModuleHigh(self.mktype(attrs={AttrId.charge_rate: 4.0}).id)
        item.charge = Charge(self.mktype().id)
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.charged_cycles)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_laser_combat(self):
        fit = Fit()
        effect = self.mkeffect(
            effect_id=EffectId.target_attack,
            category_id=EffectCategoryId.active)
        item = ModuleHigh(self.mktype(
            attrs={AttrId.capacity: 4.0},
            effects=[effect],
            default_effect=effect).id)
        item.charge = Charge(self.mktype(attrs={
            AttrId.volume: 2.0,
            AttrId.crystals_get_damaged: 1.0,
            AttrId.hp: 2.2,
            AttrId.crystal_volatility_chance: 0.1,
            AttrId.crystal_volatility_dmg: 0.01}).id)
        fit.modules.high.append(item)
        # Verification
        self.assertEqual(item.charged_cycles, 4400)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_laser_mining(self):
        fit = Fit()
        effect = self.mkeffect(
            effect_id=EffectId.mining_laser,
            category_id=EffectCategoryId.active)
        item = ModuleHigh(self.mktype(
            attrs={AttrId.capacity: 4.0},
            effects=[effect],
            default_effect=effect).id)
        item.charge = Charge(self.mktype(attrs={
            AttrId.volume: 2.0,
            AttrId.crystals_get_damaged: 1.0,
            AttrId.hp: 2.2,
            AttrId.crystal_volatility_chance: 0.1,
            AttrId.crystal_volatility_dmg: 0.01}).id)
        fit.modules.high.append(item)
        # Verification
        self.assertEqual(item.charged_cycles, 4400)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_laser_not_damageable(self):
        fit = Fit()
        effect = self.mkeffect(
            effect_id=EffectId.target_attack,
            category_id=EffectCategoryId.active)
        item = ModuleHigh(self.mktype(
            attrs={AttrId.capacity: 4.0},
            effects=[effect],
            default_effect=effect).id)
        item.charge = Charge(self.mktype(attrs={
            AttrId.volume: 2.0,
            AttrId.hp: 2.2,
            AttrId.crystal_volatility_chance: 0.1,
            AttrId.crystal_volatility_dmg: 0.01}).id)
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.charged_cycles)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_laser_no_hp(self):
        fit = Fit()
        effect = self.mkeffect(
            effect_id=EffectId.target_attack,
            category_id=EffectCategoryId.active)
        item = ModuleHigh(self.mktype(
            attrs={AttrId.capacity: 4.0},
            effects=[effect],
            default_effect=effect).id)
        item.charge = Charge(self.mktype(attrs={
            AttrId.volume: 2.0,
            AttrId.crystals_get_damaged: 1.0,
            AttrId.crystal_volatility_chance: 0.1,
            AttrId.crystal_volatility_dmg: 0.01}).id)
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.charged_cycles)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_laser_no_chance(self):
        fit = Fit()
        effect = self.mkeffect(
            effect_id=EffectId.target_attack,
            category_id=EffectCategoryId.active)
        item = ModuleHigh(self.mktype(
            attrs={AttrId.capacity: 4.0},
            effects=[effect],
            default_effect=effect).id)
        item.charge = Charge(self.mktype(attrs={
            AttrId.volume: 2.0,
            AttrId.crystals_get_damaged: 1.0,
            AttrId.hp: 2.2,
            AttrId.crystal_volatility_dmg: 0.01}).id)
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.charged_cycles)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_laser_no_dmg(self):
        fit = Fit()
        effect = self.mkeffect(
            effect_id=EffectId.target_attack,
            category_id=EffectCategoryId.active)
        item = ModuleHigh(self.mktype(
            attrs={AttrId.capacity: 4.0},
            effects=[effect],
            default_effect=effect).id)
        item.charge = Charge(self.mktype(attrs={
            AttrId.volume: 2.0,
            AttrId.crystals_get_damaged: 1.0,
            AttrId.hp: 2.2,
            AttrId.crystal_volatility_chance: 0.1}).id)
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.charged_cycles)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_default_effect(self):
        fit = Fit()
        effect = self.mkeffect(
            effect_id=EffectId.target_attack,
            category_id=EffectCategoryId.active)
        item = ModuleHigh(self.mktype(
            attrs={AttrId.capacity: 4.0},
            effects=[effect]).id)
        item.charge = Charge(self.mktype(attrs={
            AttrId.volume: 2.0,
            AttrId.crystals_get_damaged: 1.0,
            AttrId.hp: 2.2,
            AttrId.crystal_volatility_chance: 0.1,
            AttrId.crystal_volatility_dmg: 0.01}).id)
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.charged_cycles)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_source(self):
        fit = Fit()
        item = ModuleHigh(self.mktype(attrs={
            AttrId.capacity: 100.0,
            AttrId.charge_rate: 2.0}).id)
        item.charge = Charge(self.mktype(attrs={AttrId.volume: 2.0}).id)
        fit.modules.high.append(item)
        fit.source = None
        # Verification
        self.assertIsNone(item.charged_cycles)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)
