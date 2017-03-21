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


class TestItemMixinDamageBombNominalVolley(ItemMixinTestCase):

    def setUp(self):
        super().setUp()
        self.ch.attribute(attribute_id=Attribute.capacity)
        self.ch.attribute(attribute_id=Attribute.volume)
        self.ch.attribute(attribute_id=Attribute.charge_rate)
        self.ch.attribute(attribute_id=Attribute.reload_time)
        self.ch.attribute(attribute_id=Attribute.module_reactivation_delay)
        self.ch.attribute(attribute_id=Attribute.em_damage)
        self.ch.attribute(attribute_id=Attribute.thermal_damage)
        self.ch.attribute(attribute_id=Attribute.kinetic_damage)
        self.ch.attribute(attribute_id=Attribute.explosive_damage)
        self.cycle_attr = self.ch.attribute()
        self.effect_launcher = self.ch.effect(
            effect_id=Effect.use_missiles, category=EffectCategory.active, duration_attribute=self.cycle_attr.id
        )
        self.effect_bomb = self.ch.effect(effect_id=Effect.bomb_launching, category=EffectCategory.active)

    def test_generic(self):
        fit = Fit()
        launcher = ModuleHigh(self.ch.type(attributes={
            Attribute.capacity: 60.0, self.cycle_attr: 5000, Attribute.charge_rate: 1.0,
            Attribute.reload_time: 10000, Attribute.module_reactivation_delay: 120000
        }, effects=[self.effect_launcher], default_effect=self.effect_launcher).id, state=State.active)
        bomb = Charge(self.ch.type(attributes={
            Attribute.volume: 30.0, Attribute.em_damage: 5.2, Attribute.thermal_damage: 6.3,
            Attribute.kinetic_damage: 7.4, Attribute.explosive_damage: 8.5
        }, effects=[self.effect_bomb], default_effect=self.effect_bomb).id)
        launcher.charge = bomb
        fit.modules.high.append(launcher)
        # Verification
        volley = launcher.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 5.2)
        self.assertAlmostEqual(volley.thermal, 6.3)
        self.assertAlmostEqual(volley.kinetic, 7.4)
        self.assertAlmostEqual(volley.explosive, 8.5)
        self.assertAlmostEqual(volley.total, 27.4)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_multiplier(self):
        self.ch.attribute(attribute_id=Attribute.damage_multiplier)
        fit = Fit()
        launcher = ModuleHigh(self.ch.type(attributes={
            Attribute.capacity: 60.0, self.cycle_attr: 5000, Attribute.charge_rate: 1.0,
            Attribute.reload_time: 10000, Attribute.module_reactivation_delay: 120000,
            Attribute.damage_multiplier: 5.5
        }, effects=[self.effect_launcher], default_effect=self.effect_launcher).id, state=State.active)
        bomb = Charge(self.ch.type(attributes={
            Attribute.volume: 30.0, Attribute.em_damage: 5.2, Attribute.thermal_damage: 6.3,
            Attribute.kinetic_damage: 7.4, Attribute.explosive_damage: 8.5
        }, effects=[self.effect_bomb], default_effect=self.effect_bomb).id)
        launcher.charge = bomb
        fit.modules.high.append(launcher)
        # Verification
        volley = launcher.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 5.2)
        self.assertAlmostEqual(volley.thermal, 6.3)
        self.assertAlmostEqual(volley.kinetic, 7.4)
        self.assertAlmostEqual(volley.explosive, 8.5)
        self.assertAlmostEqual(volley.total, 27.4)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_insufficient_state(self):
        fit = Fit()
        launcher = ModuleHigh(self.ch.type(attributes={
            Attribute.capacity: 60.0, self.cycle_attr: 5000, Attribute.charge_rate: 1.0,
            Attribute.reload_time: 10000, Attribute.module_reactivation_delay: 120000
        }, effects=[self.effect_launcher], default_effect=self.effect_launcher).id, state=State.online)
        bomb = Charge(self.ch.type(attributes={
            Attribute.volume: 30.0, Attribute.em_damage: 5.2, Attribute.thermal_damage: 6.3,
            Attribute.kinetic_damage: 7.4, Attribute.explosive_damage: 8.5
        }, effects=[self.effect_bomb], default_effect=self.effect_bomb).id)
        launcher.charge = bomb
        fit.modules.high.append(launcher)
        # Verification
        volley = launcher.get_nominal_volley()
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertIsNone(volley.total)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_no_charge(self):
        fit = Fit()
        launcher = ModuleHigh(self.ch.type(attributes={
            Attribute.capacity: 60.0, self.cycle_attr: 5000, Attribute.charge_rate: 1.0,
            Attribute.reload_time: 10000, Attribute.module_reactivation_delay: 120000
        }, effects=[self.effect_launcher], default_effect=self.effect_launcher).id, state=State.active)
        fit.modules.high.append(launcher)
        # Verification
        volley = launcher.get_nominal_volley()
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertIsNone(volley.total)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
