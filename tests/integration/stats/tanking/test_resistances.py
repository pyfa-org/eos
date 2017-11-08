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
from eos.const.eve import AttributeId
from tests.integration.stats.stats_testcase import StatsTestCase


class TestResistances(StatsTestCase):

    def setUp(self):
        StatsTestCase.setUp(self)
        self.ch.attr(attribute_id=AttributeId.em_damage_resonance)
        self.ch.attr(attribute_id=AttributeId.thermal_damage_resonance)
        self.ch.attr(attribute_id=AttributeId.kinetic_damage_resonance)
        self.ch.attr(attribute_id=AttributeId.explosive_damage_resonance)
        self.ch.attr(attribute_id=AttributeId.armor_em_damage_resonance)
        self.ch.attr(attribute_id=AttributeId.armor_thermal_damage_resonance)
        self.ch.attr(attribute_id=AttributeId.armor_kinetic_damage_resonance)
        self.ch.attr(attribute_id=AttributeId.armor_explosive_damage_resonance)
        self.ch.attr(attribute_id=AttributeId.shield_em_damage_resonance)
        self.ch.attr(attribute_id=AttributeId.shield_thermal_damage_resonance)
        self.ch.attr(attribute_id=AttributeId.shield_kinetic_damage_resonance)
        self.ch.attr(attribute_id=AttributeId.shield_explosive_damage_resonance)

    def test_relay(self):
        # Check that stats service relays resistance stats properly
        self.fit.ship = Ship(self.ch.type(attributes={
            AttributeId.em_damage_resonance: 0.05,
            AttributeId.thermal_damage_resonance: 0.06,
            AttributeId.kinetic_damage_resonance: 0.07,
            AttributeId.explosive_damage_resonance: 0.08,
            AttributeId.armor_em_damage_resonance: 0.09,
            AttributeId.armor_thermal_damage_resonance: 0.1,
            AttributeId.armor_kinetic_damage_resonance: 0.11,
            AttributeId.armor_explosive_damage_resonance: 0.12,
            AttributeId.shield_em_damage_resonance: 0.13,
            AttributeId.shield_thermal_damage_resonance: 0.14,
            AttributeId.shield_kinetic_damage_resonance: 0.15,
            AttributeId.shield_explosive_damage_resonance: 0.16}).id)
        # Action
        res_stats = self.fit.stats.resistances
        # Verification
        self.assertAlmostEqual(res_stats.hull.em, 0.95)
        self.assertAlmostEqual(res_stats.hull.thermal, 0.94)
        self.assertAlmostEqual(res_stats.hull.kinetic, 0.93)
        self.assertAlmostEqual(res_stats.hull.explosive, 0.92)
        self.assertAlmostEqual(res_stats.armor.em, 0.91)
        self.assertAlmostEqual(res_stats.armor.thermal, 0.9)
        self.assertAlmostEqual(res_stats.armor.kinetic, 0.89)
        self.assertAlmostEqual(res_stats.armor.explosive, 0.88)
        self.assertAlmostEqual(res_stats.shield.em, 0.87)
        self.assertAlmostEqual(res_stats.shield.thermal, 0.86)
        self.assertAlmostEqual(res_stats.shield.kinetic, 0.85)
        self.assertAlmostEqual(res_stats.shield.explosive, 0.84)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_ship(self):
        # Check that something sane is returned in case of no ship
        # Action
        res_stats = self.fit.stats.resistances
        # Verification
        self.assertIsNone(res_stats.hull.em)
        self.assertIsNone(res_stats.hull.thermal)
        self.assertIsNone(res_stats.hull.kinetic)
        self.assertIsNone(res_stats.hull.explosive)
        self.assertIsNone(res_stats.armor.em)
        self.assertIsNone(res_stats.armor.thermal)
        self.assertIsNone(res_stats.armor.kinetic)
        self.assertIsNone(res_stats.armor.explosive)
        self.assertIsNone(res_stats.shield.em)
        self.assertIsNone(res_stats.shield.thermal)
        self.assertIsNone(res_stats.shield.kinetic)
        self.assertIsNone(res_stats.shield.explosive)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_source(self):
        self.fit.ship = Ship(self.ch.type(attributes={
            AttributeId.em_damage_resonance: 0.05,
            AttributeId.thermal_damage_resonance: 0.06,
            AttributeId.kinetic_damage_resonance: 0.07,
            AttributeId.explosive_damage_resonance: 0.08,
            AttributeId.armor_em_damage_resonance: 0.09,
            AttributeId.armor_thermal_damage_resonance: 0.1,
            AttributeId.armor_kinetic_damage_resonance: 0.11,
            AttributeId.armor_explosive_damage_resonance: 0.12,
            AttributeId.shield_em_damage_resonance: 0.13,
            AttributeId.shield_thermal_damage_resonance: 0.14,
            AttributeId.shield_kinetic_damage_resonance: 0.15,
            AttributeId.shield_explosive_damage_resonance: 0.16}).id)
        self.fit.source = None
        # Action
        res_stats = self.fit.stats.resistances
        # Verification
        self.assertIsNone(res_stats.hull.em)
        self.assertIsNone(res_stats.hull.thermal)
        self.assertIsNone(res_stats.hull.kinetic)
        self.assertIsNone(res_stats.hull.explosive)
        self.assertIsNone(res_stats.armor.em)
        self.assertIsNone(res_stats.armor.thermal)
        self.assertIsNone(res_stats.armor.kinetic)
        self.assertIsNone(res_stats.armor.explosive)
        self.assertIsNone(res_stats.shield.em)
        self.assertIsNone(res_stats.shield.thermal)
        self.assertIsNone(res_stats.shield.kinetic)
        self.assertIsNone(res_stats.shield.explosive)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
