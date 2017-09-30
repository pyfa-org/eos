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


class TestItemDamageDrone(ItemMixinTestCase):

    def setUp(self):
        super().setUp()
        self.ch.attribute(attribute_id=Attribute.damage_multiplier)
        self.ch.attribute(attribute_id=Attribute.em_damage)
        self.ch.attribute(attribute_id=Attribute.thermal_damage)
        self.ch.attribute(attribute_id=Attribute.kinetic_damage)
        self.ch.attribute(attribute_id=Attribute.explosive_damage)
        self.cycle_attr = self.ch.attribute()
        self.effect = self.ch.effect(
            effect_id=Effect.target_attack, category=EffectCategory.active, duration_attribute=self.cycle_attr.id
        )

    def test_nominal_volley_generic(self):
        fit = Fit()
        item = Drone(self.ch.type(attributes={
            Attribute.damage_multiplier: 2.5, Attribute.em_damage: 52, Attribute.thermal_damage: 63,
            Attribute.kinetic_damage: 74, Attribute.explosive_damage: 85, self.cycle_attr.id: 4000
        }, effects=[self.effect], default_effect=self.effect).id, state=State.active)
        fit.drones.add(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 130)
        self.assertAlmostEqual(volley.thermal, 157.5)
        self.assertAlmostEqual(volley.kinetic, 185)
        self.assertAlmostEqual(volley.explosive, 212.5)
        self.assertAlmostEqual(volley.total, 685)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_no_multiplier(self):
        fit = Fit()
        item = Drone(self.ch.type(attributes={
            Attribute.em_damage: 52, Attribute.thermal_damage: 63, Attribute.kinetic_damage: 74,
            Attribute.explosive_damage: 85, self.cycle_attr.id: 4000
        }, effects=[self.effect], default_effect=self.effect).id, state=State.active)
        fit.drones.add(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 52)
        self.assertAlmostEqual(volley.thermal, 63)
        self.assertAlmostEqual(volley.kinetic, 74)
        self.assertAlmostEqual(volley.explosive, 85)
        self.assertAlmostEqual(volley.total, 274)
        # Cleanup
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_nominal_volley_insufficient_state(self):
        fit = Fit()
        item = Drone(self.ch.type(attributes={
            Attribute.damage_multiplier: 2.5, Attribute.em_damage: 52, Attribute.thermal_damage: 63,
            Attribute.kinetic_damage: 74, Attribute.explosive_damage: 85, self.cycle_attr.id: 4000
        }, effects=[self.effect], default_effect=self.effect).id, state=State.online)
        fit.drones.add(item)
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

    def test_nominal_voley_disabled_effect(self):
        fit = Fit()
        item = Drone(self.ch.type(attributes={
            Attribute.damage_multiplier: 2.5, Attribute.em_damage: 52, Attribute.thermal_damage: 63,
            Attribute.kinetic_damage: 74, Attribute.explosive_damage: 85, self.cycle_attr.id: 4000
        }, effects=[self.effect], default_effect=self.effect).id, state=State.active)
        item.set_effect_run_mode(self.effect.id, EffectRunMode.force_stop)
        fit.drones.add(item)
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
        item = Drone(self.ch.type(attributes={
            Attribute.damage_multiplier: 2.5, Attribute.em_damage: 52, Attribute.thermal_damage: 63,
            Attribute.kinetic_damage: 74, Attribute.explosive_damage: 85, self.cycle_attr.id: 4000
        }, effects=[self.effect], default_effect=self.effect).id, state=State.active)
        fit.drones.add(item)
        # Verification
        dps = item.get_nominal_dps(reload=False)
        self.assertAlmostEqual(dps.em, 32.5)
        self.assertAlmostEqual(dps.thermal, 39.375)
        self.assertAlmostEqual(dps.kinetic, 46.25)
        self.assertAlmostEqual(dps.explosive, 53.125)
        self.assertAlmostEqual(dps.total, 171.25)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_nominal_dps_reload(self):
        fit = Fit()
        item = Drone(self.ch.type(attributes={
            Attribute.damage_multiplier: 2.5, Attribute.em_damage: 52, Attribute.thermal_damage: 63,
            Attribute.kinetic_damage: 74, Attribute.explosive_damage: 85, self.cycle_attr.id: 4000
        }, effects=[self.effect], default_effect=self.effect).id, state=State.active)
        fit.drones.add(item)
        # Verification
        dps = item.get_nominal_dps(reload=True)
        self.assertAlmostEqual(dps.em, 32.5)
        self.assertAlmostEqual(dps.thermal, 39.375)
        self.assertAlmostEqual(dps.kinetic, 46.25)
        self.assertAlmostEqual(dps.explosive, 53.125)
        self.assertAlmostEqual(dps.total, 171.25)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
