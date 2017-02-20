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


from unittest.mock import patch

from eos import *
from eos.const.eve import Attribute, Effect, EffectCategory
from tests.integration.integration_testcase import IntegrationTestCase


class TestRahResults(IntegrationTestCase):

    def setUp(self):
        super().setUp()
        # Attribute setup
        self.max_attr = self.ch.attribute(
            attribute_id=100000, default_value=1.0, high_is_good=False, stackable=False
        )
        self.cycle_attr = self.ch.attribute(
            attribute_id=100001, high_is_good=False, stackable=True
        )
        self.shift_attr = self.ch.attribute(
            attribute_id=Attribute.resistance_shift_amount, high_is_good=True, stackable=True
        )
        self.armor_em, self.armor_therm, self.armor_kin, self.armor_exp = (self.ch.attribute(
            attribute_id=attr, max_attribute=self.max_attr.id, high_is_good=False, stackable=False
        ) for attr in (
            Attribute.armor_em_damage_resonance, Attribute.armor_thermal_damage_resonance,
            Attribute.armor_kinetic_damage_resonance, Attribute.armor_explosive_damage_resonance
        ))
        # Effect setup
        self.rah_effect = self.ch.effect(
            effect_id=Effect.adaptive_armor_hardener, category=EffectCategory.active,
            duration_attribute=self.cycle_attr.id
        )

    def make_ship_type(self, type_id, resonances):
        attr_order = (self.armor_em.id, self.armor_therm.id, self.armor_kin.id, self.armor_exp.id)
        self.ch.type(type_id=type_id, attributes=dict(zip(attr_order, resonances)), effects=())

    def make_rah_type(self, type_id, resonances, shift_amount, cycle_time):
        attr_order = (
            self.armor_em.id, self.armor_therm.id, self.armor_kin.id,
            self.armor_exp.id, self.shift_attr.id, self.cycle_attr.id
        )
        self.ch.type(
            type_id=type_id, effects=(self.rah_effect,), default_effect=self.rah_effect,
            attributes=dict(zip(attr_order, (*resonances, shift_amount, cycle_time)))
        )

    @patch('eos.fit.sim.reactive_armor_hardener.MAX_SIMULATION_TICKS', new=6)
    def test_single_run(self):
        # Setup
        ship_type_id = 1
        rah_type_id = 2
        self.make_ship_type(ship_type_id, (0.5, 0.65, 0.75, 0.9))
        self.make_rah_type(rah_type_id, (0.85, 0.85, 0.85, 0.85), 6, 5)
        # Compose fit
        fit = Fit()
        ship_item = Ship(ship_type_id)
        fit.ship = ship_item
        rah_item = ModuleLow(rah_type_id, state=State.active)
        fit.modules.low.equip(rah_item)
        # Verify
        self.assertAlmostEqual(rah_item.attributes[self.armor_em.id], 1)
        self.assertAlmostEqual(rah_item.attributes[self.armor_therm.id], 0.925)
        self.assertAlmostEqual(rah_item.attributes[self.armor_kin.id], 0.82)
        self.assertAlmostEqual(rah_item.attributes[self.armor_exp.id], 0.655)
        # Cleanup
        fit.ship = None
        fit.modules.low.clear()
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    @patch('eos.fit.sim.reactive_armor_hardener.MAX_SIMULATION_TICKS', new=3)
    def test_order_multi(self):
        # Setup
        ship_type_id = 1
        rah_type_id = 2
        self.make_ship_type(ship_type_id, (0.675, 0.675, 0.675, 0.675))
        self.make_rah_type(rah_type_id, (0.85, 0.85, 0.85, 0.85), 6, 5)
        # Compose fit
        fit = Fit()
        ship_item = Ship(ship_type_id)
        fit.ship = ship_item
        rah_item = ModuleLow(rah_type_id, state=State.active)
        fit.modules.low.equip(rah_item)
        # Verify
        # From real tests, gecko vs gnosis
        # ---
        # 0 0.850 0.850 0.850 0.850
        # 1 0.910 0.790 0.790 0.910 (kin therm > em explo)
        # Loop: 0-1
        self.assertAlmostEqual(rah_item.attributes[self.armor_em.id], 0.88)
        self.assertAlmostEqual(rah_item.attributes[self.armor_therm.id], 0.82)
        self.assertAlmostEqual(rah_item.attributes[self.armor_kin.id], 0.82)
        self.assertAlmostEqual(rah_item.attributes[self.armor_exp.id], 0.88)
        # Cleanup
        fit.ship = None
        fit.modules.low.clear()
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    @patch('eos.fit.sim.reactive_armor_hardener.MAX_SIMULATION_TICKS', new=6)
    def test_order_therm_kin_exp(self):
        # Setup
        ship_type_id = 1
        rah_type_id = 2
        self.make_ship_type(ship_type_id, (0.675, 0.675, 0.675, 0.675))
        self.make_rah_type(rah_type_id, (0.85, 0.85, 0.85, 0.85), 6, 5)
        # Compose fit
        fit = Fit()
        fit.default_incoming_damage = DamageProfile(0, 1, 1, 1)
        ship_item = Ship(ship_type_id)
        fit.ship = ship_item
        rah_item = ModuleLow(rah_type_id, state=State.active)
        fit.modules.low.equip(rah_item)
        # Verify
        # From real tests, gecko vs gnosis with 2 EM hardeners
        # 0 0.850 0.850 0.850 0.850
        # 1 0.910 0.790 0.790 0.910 (kin therm > explo)
        # 2 0.970 0.730 0.850 0.850 (therm > kin)
        # ---
        # 3 1.000 0.790 0.805 0.805
        # 4 1.000 0.850 0.775 0.775
        # 5 1.000 0.820 0.745 0.835 (kin > explo)
        # Loop: 3-5
        self.assertAlmostEqual(rah_item.attributes[self.armor_em.id], 1)
        self.assertAlmostEqual(rah_item.attributes[self.armor_therm.id], 0.82)
        self.assertAlmostEqual(rah_item.attributes[self.armor_kin.id], 0.775)
        self.assertAlmostEqual(rah_item.attributes[self.armor_exp.id], 0.805)
        # Cleanup
        fit.ship = None
        fit.modules.low.clear()
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    @patch('eos.fit.sim.reactive_armor_hardener.MAX_SIMULATION_TICKS', new=6)
    def test_order_em_kin_exp(self):
        # Setup
        ship_type_id = 1
        rah_type_id = 2
        self.make_ship_type(ship_type_id, (0.675, 0.675, 0.675, 0.675))
        self.make_rah_type(rah_type_id, (0.85, 0.85, 0.85, 0.85), 6, 5)
        # Compose fit
        fit = Fit()
        fit.default_incoming_damage = DamageProfile(1, 0, 1, 1)
        ship_item = Ship(ship_type_id)
        fit.ship = ship_item
        rah_item = ModuleLow(rah_type_id, state=State.active)
        fit.modules.low.equip(rah_item)
        # Verify
        # From real tests, gecko vs gnosis with 2 thermal hardeners
        # 0 0.850 0.850 0.850 0.850
        # 1 0.910 0.910 0.790 0.790 (kin explo > em)
        # 2 0.850 0.970 0.730 0.850 (kin > explo)
        # ---
        # 3 0.805 1.000 0.790 0.805
        # 4 0.775 1.000 0.850 0.775
        # 5 0.835 1.000 0.820 0.745 (explo > em)
        # Loop: 3-5
        self.assertAlmostEqual(rah_item.attributes[self.armor_em.id], 0.805)
        self.assertAlmostEqual(rah_item.attributes[self.armor_therm.id], 1)
        self.assertAlmostEqual(rah_item.attributes[self.armor_kin.id], 0.82)
        self.assertAlmostEqual(rah_item.attributes[self.armor_exp.id], 0.775)
        # Cleanup
        fit.ship = None
        fit.modules.low.clear()
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    @patch('eos.fit.sim.reactive_armor_hardener.MAX_SIMULATION_TICKS', new=6)
    def test_order_em_therm_exp(self):
        # Setup
        ship_type_id = 1
        rah_type_id = 2
        self.make_ship_type(ship_type_id, (0.675, 0.675, 0.675, 0.675))
        self.make_rah_type(rah_type_id, (0.85, 0.85, 0.85, 0.85), 6, 5)
        # Compose fit
        fit = Fit()
        fit.default_incoming_damage = DamageProfile(1, 1, 0, 1)
        ship_item = Ship(ship_type_id)
        fit.ship = ship_item
        rah_item = ModuleLow(rah_type_id, state=State.active)
        fit.modules.low.equip(rah_item)
        # Verify
        # From real tests, gecko vs gnosis with 2 kinetic hardeners
        # 0 0.850 0.850 0.850 0.850
        # 1 0.910 0.790 0.910 0.790 (explo therm > em)
        # 2 0.850 0.730 0.970 0.850 (therm > explo)
        # ---
        # 3 0.805 0.790 1.000 0.805
        # 4 0.775 0.850 1.000 0.775
        # 5 0.835 0.820 1.000 0.745 (explo > em)
        # Loop: 3-5
        self.assertAlmostEqual(rah_item.attributes[self.armor_em.id], 0.805)
        self.assertAlmostEqual(rah_item.attributes[self.armor_therm.id], 0.82)
        self.assertAlmostEqual(rah_item.attributes[self.armor_kin.id], 1)
        self.assertAlmostEqual(rah_item.attributes[self.armor_exp.id], 0.775)
        # Cleanup
        fit.ship = None
        fit.modules.low.clear()
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    @patch('eos.fit.sim.reactive_armor_hardener.MAX_SIMULATION_TICKS', new=6)
    def test_order_em_therm_kin(self):
        # Setup
        ship_type_id = 1
        rah_type_id = 2
        self.make_ship_type(ship_type_id, (0.675, 0.675, 0.675, 0.675))
        self.make_rah_type(rah_type_id, (0.85, 0.85, 0.85, 0.85), 6, 5)
        # Compose fit
        fit = Fit()
        fit.default_incoming_damage = DamageProfile(1, 1, 1, 0)
        ship_item = Ship(ship_type_id)
        fit.ship = ship_item
        rah_item = ModuleLow(rah_type_id, state=State.active)
        fit.modules.low.equip(rah_item)
        # Verify
        # From real tests, gecko vs gnosis with 2 explosive hardeners
        # 0 0.850 0.850 0.850 0.850
        # 1 0.910 0.790 0.790 0.910 (kin therm > em)
        # 2 0.850 0.730 0.850 0.970 (therm > kin)
        # ---
        # 3 0.805 0.790 0.805 1.000
        # 4 0.775 0.850 0.775 1.000
        # 5 0.835 0.820 0.745 1.000 (kin > em)
        # Loop: 3-5
        self.assertAlmostEqual(rah_item.attributes[self.armor_em.id], 0.805)
        self.assertAlmostEqual(rah_item.attributes[self.armor_therm.id], 0.82)
        self.assertAlmostEqual(rah_item.attributes[self.armor_kin.id], 0.775)
        self.assertAlmostEqual(rah_item.attributes[self.armor_exp.id], 1)
        # Cleanup
        fit.ship = None
        fit.modules.low.clear()
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
