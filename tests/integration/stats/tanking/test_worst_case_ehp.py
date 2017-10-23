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
from eos.const.eve import Attribute
from tests.integration.stats.stat_testcase import StatTestCase


class TestWorstCaseEhp(StatTestCase):

    def setUp(self):
        super().setUp()
        self.ch.attr(attribute_id=Attribute.hp)
        self.ch.attr(attribute_id=Attribute.em_damage_resonance)
        self.ch.attr(attribute_id=Attribute.thermal_damage_resonance)
        self.ch.attr(attribute_id=Attribute.kinetic_damage_resonance)
        self.ch.attr(attribute_id=Attribute.explosive_damage_resonance)
        self.ch.attr(attribute_id=Attribute.armor_hp)
        self.ch.attr(attribute_id=Attribute.armor_em_damage_resonance)
        self.ch.attr(attribute_id=Attribute.armor_thermal_damage_resonance)
        self.ch.attr(attribute_id=Attribute.armor_kinetic_damage_resonance)
        self.ch.attr(attribute_id=Attribute.armor_explosive_damage_resonance)
        self.ch.attr(attribute_id=Attribute.shield_capacity)
        self.ch.attr(attribute_id=Attribute.shield_em_damage_resonance)
        self.ch.attr(attribute_id=Attribute.shield_thermal_damage_resonance)
        self.ch.attr(attribute_id=Attribute.shield_kinetic_damage_resonance)
        self.ch.attr(attribute_id=Attribute.shield_explosive_damage_resonance)

    def test_relay(self):
        # Check that stats service relays wcehp stats properly
        self.fit.ship = Ship(self.ch.type(attributes={
            Attribute.hp: 10,
            Attribute.em_damage_resonance: 0.8,
            Attribute.thermal_damage_resonance: 0.5,
            Attribute.kinetic_damage_resonance: 0.5,
            Attribute.explosive_damage_resonance: 0.5,
            Attribute.armor_hp: 15,
            Attribute.armor_em_damage_resonance: 0.5,
            Attribute.armor_thermal_damage_resonance: 0.8,
            Attribute.armor_kinetic_damage_resonance: 0.5,
            Attribute.armor_explosive_damage_resonance: 0.5,
            Attribute.shield_capacity: 20,
            Attribute.shield_em_damage_resonance: 0.5,
            Attribute.shield_thermal_damage_resonance: 0.5,
            Attribute.shield_kinetic_damage_resonance: 0.65,
            Attribute.shield_explosive_damage_resonance: 0.8}).id)
        # Action
        worst_ehp_stats = self.fit.stats.worst_case_ehp
        # Verification
        self.assertAlmostEqual(worst_ehp_stats.hull, 12.5)
        self.assertAlmostEqual(worst_ehp_stats.armor, 18.75)
        self.assertAlmostEqual(worst_ehp_stats.shield, 25)
        self.assertAlmostEqual(worst_ehp_stats.total, 56.25)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_ship(self):
        # Check that something sane is returned in case of no ship
        # Action
        worst_ehp_stats = self.fit.stats.worst_case_ehp
        # Verification
        self.assertIsNone(worst_ehp_stats.hull)
        self.assertIsNone(worst_ehp_stats.armor)
        self.assertIsNone(worst_ehp_stats.shield)
        self.assertIsNone(worst_ehp_stats.total)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_source(self):
        # Check that stats service relays wcehp stats properly
        self.fit.ship = Ship(self.ch.type(attributes={
            Attribute.hp: 10,
            Attribute.em_damage_resonance: 0.8,
            Attribute.thermal_damage_resonance: 0.5,
            Attribute.kinetic_damage_resonance: 0.5,
            Attribute.explosive_damage_resonance: 0.5,
            Attribute.armor_hp: 15,
            Attribute.armor_em_damage_resonance: 0.5,
            Attribute.armor_thermal_damage_resonance: 0.8,
            Attribute.armor_kinetic_damage_resonance: 0.5,
            Attribute.armor_explosive_damage_resonance: 0.5,
            Attribute.shield_capacity: 20,
            Attribute.shield_em_damage_resonance: 0.5,
            Attribute.shield_thermal_damage_resonance: 0.5,
            Attribute.shield_kinetic_damage_resonance: 0.65,
            Attribute.shield_explosive_damage_resonance: 0.8}).id)
        self.fit.source = None
        # Action
        worst_ehp_stats = self.fit.stats.worst_case_ehp
        # Verification
        self.assertIsNone(worst_ehp_stats.hull)
        self.assertIsNone(worst_ehp_stats.armor)
        self.assertIsNone(worst_ehp_stats.shield)
        self.assertIsNone(worst_ehp_stats.total)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
