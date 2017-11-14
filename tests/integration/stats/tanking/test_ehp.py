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
from eos.const.eve import AttrId
from tests.integration.stats.stats_testcase import StatsTestCase


class TestEhp(StatsTestCase):

    def setUp(self):
        StatsTestCase.setUp(self)
        self.ch.attr(attr_id=AttrId.hp)
        self.ch.attr(attr_id=AttrId.em_dmg_resonance)
        self.ch.attr(attr_id=AttrId.thermal_dmg_resonance)
        self.ch.attr(attr_id=AttrId.kinetic_dmg_resonance)
        self.ch.attr(attr_id=AttrId.explosive_dmg_resonance)
        self.ch.attr(attr_id=AttrId.armor_hp)
        self.ch.attr(attr_id=AttrId.armor_em_dmg_resonance)
        self.ch.attr(attr_id=AttrId.armor_thermal_dmg_resonance)
        self.ch.attr(attr_id=AttrId.armor_kinetic_dmg_resonance)
        self.ch.attr(attr_id=AttrId.armor_explosive_dmg_resonance)
        self.ch.attr(attr_id=AttrId.shield_capacity)
        self.ch.attr(attr_id=AttrId.shield_em_dmg_resonance)
        self.ch.attr(attr_id=AttrId.shield_thermal_dmg_resonance)
        self.ch.attr(attr_id=AttrId.shield_kinetic_dmg_resonance)
        self.ch.attr(attr_id=AttrId.shield_explosive_dmg_resonance)

    def test_relay(self):
        # Check that stats service relays ehp stats properly
        self.fit.ship = Ship(self.ch.type(attrs={
            AttrId.hp: 10,
            AttrId.em_dmg_resonance: 0.5,
            AttrId.thermal_dmg_resonance: 0.5,
            AttrId.kinetic_dmg_resonance: 0.5,
            AttrId.explosive_dmg_resonance: 0.5,
            AttrId.armor_hp: 15,
            AttrId.armor_em_dmg_resonance: 0.5,
            AttrId.armor_thermal_dmg_resonance: 0.5,
            AttrId.armor_kinetic_dmg_resonance: 0.5,
            AttrId.armor_explosive_dmg_resonance: 0.5,
            AttrId.shield_capacity: 20,
            AttrId.shield_em_dmg_resonance: 0.5,
            AttrId.shield_thermal_dmg_resonance: 0.5,
            AttrId.shield_kinetic_dmg_resonance: 0.5,
            AttrId.shield_explosive_dmg_resonance: 0.5}).id)
        # Action
        ehp_stats = self.fit.stats.get_ehp(
            DmgProfile(em=1, thermal=1, kinetic=1, explosive=1))
        # Verification
        self.assertAlmostEqual(ehp_stats.hull, 20)
        self.assertAlmostEqual(ehp_stats.armor, 30)
        self.assertAlmostEqual(ehp_stats.shield, 40)
        self.assertAlmostEqual(ehp_stats.total, 90)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_ship(self):
        # Check that something sane is returned in case of no ship
        # Action
        ehp_stats = self.fit.stats.get_ehp(
            DmgProfile(em=1, thermal=1, kinetic=1, explosive=1))
        # Verification
        self.assertIsNone(ehp_stats.hull)
        self.assertIsNone(ehp_stats.armor)
        self.assertIsNone(ehp_stats.shield)
        self.assertIsNone(ehp_stats.total)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_source(self):
        self.fit.ship = Ship(self.ch.type(attrs={
            AttrId.hp: 10,
            AttrId.em_dmg_resonance: 0.5,
            AttrId.thermal_dmg_resonance: 0.5,
            AttrId.kinetic_dmg_resonance: 0.5,
            AttrId.explosive_dmg_resonance: 0.5,
            AttrId.armor_hp: 15,
            AttrId.armor_em_dmg_resonance: 0.5,
            AttrId.armor_thermal_dmg_resonance: 0.5,
            AttrId.armor_kinetic_dmg_resonance: 0.5,
            AttrId.armor_explosive_dmg_resonance: 0.5,
            AttrId.shield_capacity: 20,
            AttrId.shield_em_dmg_resonance: 0.5,
            AttrId.shield_thermal_dmg_resonance: 0.5,
            AttrId.shield_kinetic_dmg_resonance: 0.5,
            AttrId.shield_explosive_dmg_resonance: 0.5}).id)
        self.fit.source = None
        # Action
        ehp_stats = self.fit.stats.get_ehp(
            DmgProfile(em=1, thermal=1, kinetic=1, explosive=1))
        # Verification
        self.assertIsNone(ehp_stats.hull)
        self.assertIsNone(ehp_stats.armor)
        self.assertIsNone(ehp_stats.shield)
        self.assertIsNone(ehp_stats.total)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
