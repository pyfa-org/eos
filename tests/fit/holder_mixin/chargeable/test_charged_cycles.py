# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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
from eos.fit.holder.item import ModuleHigh, Charge
from tests.fit.fit_testcase import FitTestCase


class TestHolderMixinChargedCycles(FitTestCase):

    def setUp(self):
        super().setUp()
        self.holder = ModuleHigh(type_id=None)
        self.holder.item = Mock()
        self.holder.item.attributes = {}
        self.holder.attributes = {}
        self.charge = Charge(type_id=None)
        self.charge.item = Mock()
        self.charge.item.attributes = {}
        self.charge.attributes = {}
        self.holder.charge = self.charge

    def test_ammo_generic(self):
        self.holder.attributes[Attribute.capacity] = 100.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.holder.item.attributes[Attribute.charge_rate] = 1.0
        self.holder.attributes[Attribute.charge_rate] = 2.0
        self.assertEqual(self.holder.fully_charged_cycles, 25)
        self.assertEqual(self.holder.fully_charged_cycles_max, 25)

    def test_ammo_override(self):
        self.holder.attributes[Attribute.capacity] = 100.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.holder.charge_quantity = 40
        self.holder.item.attributes[Attribute.charge_rate] = 1.0
        self.holder.attributes[Attribute.charge_rate] = 2.0
        self.assertEqual(self.holder.fully_charged_cycles, 20)
        self.assertEqual(self.holder.fully_charged_cycles_max, 25)

    def test_ammo_round_down(self):
        self.holder.attributes[Attribute.capacity] = 22.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.holder.item.attributes[Attribute.charge_rate] = 1.0
        self.holder.attributes[Attribute.charge_rate] = 4.0
        self.assertEqual(self.holder.fully_charged_cycles, 2)
        self.assertEqual(self.holder.fully_charged_cycles_max, 2)

    def test_ammo_no_quantity(self):
        self.holder.item.attributes[Attribute.charge_rate] = 1.0
        self.holder.attributes[Attribute.charge_rate] = 4.0
        self.assertIsNone(self.holder.fully_charged_cycles)
        self.assertIsNone(self.holder.fully_charged_cycles_max)

    def test_laser_combat(self):
        self.holder.attributes[Attribute.capacity] = 4.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.charge.attributes[Attribute.crystals_get_damaged] = 1.0
        self.charge.attributes[Attribute.hp] = 2.2
        self.charge.attributes[Attribute.crystal_volatility_chance] = 0.1
        self.charge.attributes[Attribute.crystal_volatility_damage] = 0.01
        self.holder.item.default_effect.id = Effect.target_attack
        self.assertEqual(self.holder.fully_charged_cycles, 4400)
        self.assertEqual(self.holder.fully_charged_cycles_max, 4400)

    def test_laser_mining(self):
        self.holder.attributes[Attribute.capacity] = 4.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.charge.attributes[Attribute.crystals_get_damaged] = 1.0
        self.charge.attributes[Attribute.hp] = 2.2
        self.charge.attributes[Attribute.crystal_volatility_chance] = 0.1
        self.charge.attributes[Attribute.crystal_volatility_damage] = 0.01
        self.holder.item.default_effect.id = Effect.mining_laser
        self.assertEqual(self.holder.fully_charged_cycles, 4400)
        self.assertEqual(self.holder.fully_charged_cycles_max, 4400)

    def test_laser_not_damageable(self):
        self.holder.attributes[Attribute.capacity] = 4.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.charge.attributes[Attribute.hp] = 2.2
        self.charge.attributes[Attribute.crystal_volatility_chance] = 0.1
        self.charge.attributes[Attribute.crystal_volatility_damage] = 0.01
        self.holder.item.default_effect.id = Effect.target_attack
        self.assertIsNone(self.holder.fully_charged_cycles)
        self.assertIsNone(self.holder.fully_charged_cycles_max)

    def test_laser_no_hp(self):
        self.holder.attributes[Attribute.capacity] = 4.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.charge.attributes[Attribute.crystals_get_damaged] = 1.0
        self.charge.attributes[Attribute.crystal_volatility_chance] = 0.1
        self.charge.attributes[Attribute.crystal_volatility_damage] = 0.01
        self.holder.item.default_effect.id = Effect.target_attack
        self.assertIsNone(self.holder.fully_charged_cycles)
        self.assertIsNone(self.holder.fully_charged_cycles_max)

    def test_laser_no_chance(self):
        self.holder.attributes[Attribute.capacity] = 4.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.charge.attributes[Attribute.crystals_get_damaged] = 1.0
        self.charge.attributes[Attribute.hp] = 2.2
        self.charge.attributes[Attribute.crystal_volatility_damage] = 0.01
        self.holder.item.default_effect.id = Effect.target_attack
        self.assertIsNone(self.holder.fully_charged_cycles)
        self.assertIsNone(self.holder.fully_charged_cycles_max)

    def test_laser_no_damage(self):
        self.holder.attributes[Attribute.capacity] = 4.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.charge.attributes[Attribute.crystals_get_damaged] = 1.0
        self.charge.attributes[Attribute.hp] = 2.2
        self.charge.attributes[Attribute.crystal_volatility_chance] = 0.1
        self.holder.item.default_effect.id = Effect.target_attack
        self.assertIsNone(self.holder.fully_charged_cycles)
        self.assertIsNone(self.holder.fully_charged_cycles_max)

    def test_laser_override(self):
        self.holder.attributes[Attribute.capacity] = 4.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.holder.charge_quantity = 3
        self.charge.attributes[Attribute.crystals_get_damaged] = 1.0
        self.charge.attributes[Attribute.hp] = 2.2
        self.charge.attributes[Attribute.crystal_volatility_chance] = 0.1
        self.charge.attributes[Attribute.crystal_volatility_damage] = 0.01
        self.holder.item.default_effect.id = Effect.target_attack
        self.assertEqual(self.holder.fully_charged_cycles, 6600)
        self.assertEqual(self.holder.fully_charged_cycles_max, 4400)

    def test_no_item(self):
        self.holder.attributes[Attribute.capacity] = 100.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.holder.item = None
        self.holder.attributes[Attribute.charge_rate] = 2.0
        self.assertIsNone(self.holder.fully_charged_cycles)
        self.assertIsNone(self.holder.fully_charged_cycles_max)

    def test_no_default_effect(self):
        self.holder.attributes[Attribute.capacity] = 100.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.holder.item.default_effect = None
        self.holder.attributes[Attribute.charge_rate] = 2.0
        self.assertIsNone(self.holder.fully_charged_cycles)
        self.assertIsNone(self.holder.fully_charged_cycles_max)

    def test_cache(self):
        self.holder.attributes[Attribute.capacity] = 100.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.holder.item.attributes[Attribute.charge_rate] = 1.0
        self.holder.attributes[Attribute.charge_rate] = 2.0
        self.assertEqual(self.holder.fully_charged_cycles, 25)
        self.assertEqual(self.holder.fully_charged_cycles_max, 25)
        del self.holder.item.attributes[Attribute.charge_rate]
        del self.holder.attributes[Attribute.charge_rate]
        self.holder.attributes[Attribute.capacity] = 4.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.charge.attributes[Attribute.crystals_get_damaged] = 1.0
        self.charge.attributes[Attribute.hp] = 2.2
        self.charge.attributes[Attribute.crystal_volatility_chance] = 0.1
        self.charge.attributes[Attribute.crystal_volatility_damage] = 0.01
        self.holder.item._effect_ids = (Effect.target_attack,)
        self.assertEqual(self.holder.fully_charged_cycles, 25)
        self.assertEqual(self.holder.fully_charged_cycles_max, 25)

    def test_cache_volatility(self):
        self.holder.attributes[Attribute.capacity] = 100.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.holder.item.attributes[Attribute.charge_rate] = 1.0
        self.holder.attributes[Attribute.charge_rate] = 2.0
        self.assertEqual(self.holder.fully_charged_cycles, 25)
        self.assertEqual(self.holder.fully_charged_cycles_max, 25)
        self.holder._clear_volatile_attrs()
        del self.holder.item.attributes[Attribute.charge_rate]
        del self.holder.attributes[Attribute.charge_rate]
        self.holder.attributes[Attribute.capacity] = 4.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.charge.attributes[Attribute.crystals_get_damaged] = 1.0
        self.charge.attributes[Attribute.hp] = 2.2
        self.charge.attributes[Attribute.crystal_volatility_chance] = 0.1
        self.charge.attributes[Attribute.crystal_volatility_damage] = 0.01
        self.holder.item.default_effect.id = Effect.target_attack
        self.assertEqual(self.holder.fully_charged_cycles, 4400)
        self.assertEqual(self.holder.fully_charged_cycles_max, 4400)
