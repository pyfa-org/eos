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


from unittest.mock import Mock

from eos.const.eve import Attribute, Effect
from eos.fit.item import ModuleHigh, Charge
from tests.item.item_testcase import ItemMixinTestCase


class TestItemMixinChargedCycles(ItemMixinTestCase):

    def setUp(self):
        super().setUp()
        self.item = ModuleHigh(type_id=None)
        self.item._eve_type = Mock()
        self.item._eve_type.attributes = {}
        self.item.attributes = {}
        self.charge = Charge(type_id=None)
        self.charge._eve_type = Mock()
        self.charge._eve_type.attributes = {}
        self.charge.attributes = {}
        self.item.charge = self.charge

    def test_ammo_generic(self):
        self.item.attributes[Attribute.capacity] = 100.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.item._eve_type.attributes[Attribute.charge_rate] = 1.0
        self.item.attributes[Attribute.charge_rate] = 2.0
        self.assertEqual(self.item.charged_cycles, 25)

    def test_ammo_round_down(self):
        self.item.attributes[Attribute.capacity] = 22.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.item._eve_type.attributes[Attribute.charge_rate] = 1.0
        self.item.attributes[Attribute.charge_rate] = 4.0
        self.assertEqual(self.item.charged_cycles, 2)

    def test_ammo_no_quantity(self):
        self.item._eve_type.attributes[Attribute.charge_rate] = 1.0
        self.item.attributes[Attribute.charge_rate] = 4.0
        self.assertIsNone(self.item.charged_cycles)

    def test_laser_combat(self):
        self.item.attributes[Attribute.capacity] = 4.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.charge.attributes[Attribute.crystals_get_damaged] = 1.0
        self.charge.attributes[Attribute.hp] = 2.2
        self.charge.attributes[Attribute.crystal_volatility_chance] = 0.1
        self.charge.attributes[Attribute.crystal_volatility_damage] = 0.01
        self.item._eve_type.default_effect.id = Effect.target_attack
        self.assertEqual(self.item.charged_cycles, 4400)

    def test_laser_mining(self):
        self.item.attributes[Attribute.capacity] = 4.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.charge.attributes[Attribute.crystals_get_damaged] = 1.0
        self.charge.attributes[Attribute.hp] = 2.2
        self.charge.attributes[Attribute.crystal_volatility_chance] = 0.1
        self.charge.attributes[Attribute.crystal_volatility_damage] = 0.01
        self.item._eve_type.default_effect.id = Effect.mining_laser
        self.assertEqual(self.item.charged_cycles, 4400)

    def test_laser_not_damageable(self):
        self.item.attributes[Attribute.capacity] = 4.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.charge.attributes[Attribute.hp] = 2.2
        self.charge.attributes[Attribute.crystal_volatility_chance] = 0.1
        self.charge.attributes[Attribute.crystal_volatility_damage] = 0.01
        self.item._eve_type.default_effect.id = Effect.target_attack
        self.assertIsNone(self.item.charged_cycles)

    def test_laser_no_hp(self):
        self.item.attributes[Attribute.capacity] = 4.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.charge.attributes[Attribute.crystals_get_damaged] = 1.0
        self.charge.attributes[Attribute.crystal_volatility_chance] = 0.1
        self.charge.attributes[Attribute.crystal_volatility_damage] = 0.01
        self.item._eve_type.default_effect.id = Effect.target_attack
        self.assertIsNone(self.item.charged_cycles)

    def test_laser_no_chance(self):
        self.item.attributes[Attribute.capacity] = 4.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.charge.attributes[Attribute.crystals_get_damaged] = 1.0
        self.charge.attributes[Attribute.hp] = 2.2
        self.charge.attributes[Attribute.crystal_volatility_damage] = 0.01
        self.item._eve_type.default_effect.id = Effect.target_attack
        self.assertIsNone(self.item.charged_cycles)

    def test_laser_no_damage(self):
        self.item.attributes[Attribute.capacity] = 4.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.charge.attributes[Attribute.crystals_get_damaged] = 1.0
        self.charge.attributes[Attribute.hp] = 2.2
        self.charge.attributes[Attribute.crystal_volatility_chance] = 0.1
        self.item._eve_type.default_effect.id = Effect.target_attack
        self.assertIsNone(self.item.charged_cycles)

    def test_no_default_effect(self):
        self.item.attributes[Attribute.capacity] = 100.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.item._eve_type.default_effect = None
        self.item.attributes[Attribute.charge_rate] = 2.0
        self.assertIsNone(self.item.charged_cycles)

    def test_cache(self):
        self.item.attributes[Attribute.capacity] = 100.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.item._eve_type.attributes[Attribute.charge_rate] = 1.0
        self.item.attributes[Attribute.charge_rate] = 2.0
        self.assertEqual(self.item.charged_cycles, 25)
        del self.item._eve_type.attributes[Attribute.charge_rate]
        del self.item.attributes[Attribute.charge_rate]
        self.item.attributes[Attribute.capacity] = 4.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.charge.attributes[Attribute.crystals_get_damaged] = 1.0
        self.charge.attributes[Attribute.hp] = 2.2
        self.charge.attributes[Attribute.crystal_volatility_chance] = 0.1
        self.charge.attributes[Attribute.crystal_volatility_damage] = 0.01
        self.item._eve_type._effect_ids = (Effect.target_attack,)
        self.assertEqual(self.item.charged_cycles, 25)

    def test_cache_volatility(self):
        self.item.attributes[Attribute.capacity] = 100.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.item._eve_type.attributes[Attribute.charge_rate] = 1.0
        self.item.attributes[Attribute.charge_rate] = 2.0
        self.assertEqual(self.item.charged_cycles, 25)
        self.item._clear_volatile_attrs()
        del self.item._eve_type.attributes[Attribute.charge_rate]
        del self.item.attributes[Attribute.charge_rate]
        self.item.attributes[Attribute.capacity] = 4.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.charge.attributes[Attribute.crystals_get_damaged] = 1.0
        self.charge.attributes[Attribute.hp] = 2.2
        self.charge.attributes[Attribute.crystal_volatility_chance] = 0.1
        self.charge.attributes[Attribute.crystal_volatility_damage] = 0.01
        self.item._eve_type.default_effect.id = Effect.target_attack
        self.assertEqual(self.item.charged_cycles, 4400)
