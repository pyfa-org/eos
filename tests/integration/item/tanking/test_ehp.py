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
from tests.integration.item.item_testcase import ItemMixinTestCase


class TestItemMixinTankingEhp(ItemMixinTestCase):

    def setUp(self):
        ItemMixinTestCase.setUp(self)
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

    def test_uniform(self):
        fit = Fit()
        item = Ship(self.ch.type(attrs={
            AttrId.hp: 1,
            AttrId.em_dmg_resonance: 0.8,
            AttrId.thermal_dmg_resonance: 0.8,
            AttrId.kinetic_dmg_resonance: 0.8,
            AttrId.explosive_dmg_resonance: 0.8,
            AttrId.armor_hp: 10,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_thermal_dmg_resonance: 0.4,
            AttrId.armor_kinetic_dmg_resonance: 0.4,
            AttrId.armor_explosive_dmg_resonance: 0.4,
            AttrId.shield_capacity: 100,
            AttrId.shield_em_dmg_resonance: 0.2,
            AttrId.shield_thermal_dmg_resonance: 0.2,
            AttrId.shield_kinetic_dmg_resonance: 0.2,
            AttrId.shield_explosive_dmg_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        results = item.get_ehp(
            DmgProfile(em=1, thermal=1, kinetic=1, explosive=1))
        self.assertAlmostEqual(results.hull, 1.25)
        self.assertAlmostEqual(results.armor, 25)
        self.assertAlmostEqual(results.shield, 500)
        self.assertAlmostEqual(results.total, 526.25)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_non_uniform(self):
        fit = Fit()
        item = Ship(self.ch.type(attrs={
            AttrId.hp: 10,
            AttrId.em_dmg_resonance: 0.9,
            AttrId.thermal_dmg_resonance: 0.8,
            AttrId.kinetic_dmg_resonance: 0.7,
            AttrId.explosive_dmg_resonance: 0.6,
            AttrId.armor_hp: 50,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_thermal_dmg_resonance: 0.6,
            AttrId.armor_kinetic_dmg_resonance: 0.8,
            AttrId.armor_explosive_dmg_resonance: 0.9,
            AttrId.shield_capacity: 600,
            AttrId.shield_em_dmg_resonance: 1.0,
            AttrId.shield_thermal_dmg_resonance: 0.8,
            AttrId.shield_kinetic_dmg_resonance: 0.6,
            AttrId.shield_explosive_dmg_resonance: 0.5}).id)
        fit.ship = item
        # Verification
        results = item.get_ehp(
            DmgProfile(em=25, thermal=6, kinetic=8.333, explosive=1))
        self.assertAlmostEqual(results.hull, 11.957, places=3)
        self.assertAlmostEqual(results.armor, 95.276, places=3)
        self.assertAlmostEqual(results.shield, 685.551, places=3)
        self.assertAlmostEqual(results.total, 792.783, places=3)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_hp_hull(self):
        fit = Fit()
        item = Ship(self.ch.type(attrs={
            AttrId.em_dmg_resonance: 0.9,
            AttrId.thermal_dmg_resonance: 0.8,
            AttrId.kinetic_dmg_resonance: 0.7,
            AttrId.explosive_dmg_resonance: 0.6,
            AttrId.armor_hp: 50,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_thermal_dmg_resonance: 0.6,
            AttrId.armor_kinetic_dmg_resonance: 0.8,
            AttrId.armor_explosive_dmg_resonance: 0.9,
            AttrId.shield_capacity: 600,
            AttrId.shield_em_dmg_resonance: 1.0,
            AttrId.shield_thermal_dmg_resonance: 0.8,
            AttrId.shield_kinetic_dmg_resonance: 0.6,
            AttrId.shield_explosive_dmg_resonance: 0.5}).id)
        fit.ship = item
        # Verification
        results = item.get_ehp(
            DmgProfile(em=25, thermal=6, kinetic=8.333, explosive=1))
        self.assertIsNone(results.hull)
        self.assertAlmostEqual(results.armor, 95.276, places=3)
        self.assertAlmostEqual(results.shield, 685.551, places=3)
        self.assertAlmostEqual(results.total, 780.827, places=3)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_hp_armor(self):
        fit = Fit()
        item = Ship(self.ch.type(attrs={
            AttrId.hp: 10,
            AttrId.em_dmg_resonance: 0.9,
            AttrId.thermal_dmg_resonance: 0.8,
            AttrId.kinetic_dmg_resonance: 0.7,
            AttrId.explosive_dmg_resonance: 0.6,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_thermal_dmg_resonance: 0.6,
            AttrId.armor_kinetic_dmg_resonance: 0.8,
            AttrId.armor_explosive_dmg_resonance: 0.9,
            AttrId.shield_capacity: 600,
            AttrId.shield_em_dmg_resonance: 1.0,
            AttrId.shield_thermal_dmg_resonance: 0.8,
            AttrId.shield_kinetic_dmg_resonance: 0.6,
            AttrId.shield_explosive_dmg_resonance: 0.5}).id)
        fit.ship = item
        # Verification
        results = item.get_ehp(
            DmgProfile(em=25, thermal=6, kinetic=8.333, explosive=1))
        self.assertAlmostEqual(results.hull, 11.957, places=3)
        self.assertIsNone(results.armor)
        self.assertAlmostEqual(results.shield, 685.551, places=3)
        self.assertAlmostEqual(results.total, 697.507, places=3)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_hp_shield(self):
        fit = Fit()
        item = Ship(self.ch.type(attrs={
            AttrId.hp: 10,
            AttrId.em_dmg_resonance: 0.9,
            AttrId.thermal_dmg_resonance: 0.8,
            AttrId.kinetic_dmg_resonance: 0.7,
            AttrId.explosive_dmg_resonance: 0.6,
            AttrId.armor_hp: 50,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_thermal_dmg_resonance: 0.6,
            AttrId.armor_kinetic_dmg_resonance: 0.8,
            AttrId.armor_explosive_dmg_resonance: 0.9,
            AttrId.shield_em_dmg_resonance: 1.0,
            AttrId.shield_thermal_dmg_resonance: 0.8,
            AttrId.shield_kinetic_dmg_resonance: 0.6,
            AttrId.shield_explosive_dmg_resonance: 0.5}).id)
        fit.ship = item
        # Verification
        results = item.get_ehp(
            DmgProfile(em=25, thermal=6, kinetic=8.333, explosive=1))
        self.assertAlmostEqual(results.hull, 11.957, places=3)
        self.assertAlmostEqual(results.armor, 95.276, places=3)
        self.assertIsNone(results.shield)
        self.assertAlmostEqual(results.total, 107.233, places=3)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_hp_all(self):
        fit = Fit()
        item = Ship(self.ch.type(attrs={
            AttrId.em_dmg_resonance: 0.9,
            AttrId.thermal_dmg_resonance: 0.8,
            AttrId.kinetic_dmg_resonance: 0.7,
            AttrId.explosive_dmg_resonance: 0.6,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_thermal_dmg_resonance: 0.6,
            AttrId.armor_kinetic_dmg_resonance: 0.8,
            AttrId.armor_explosive_dmg_resonance: 0.9,
            AttrId.shield_em_dmg_resonance: 1.0,
            AttrId.shield_thermal_dmg_resonance: 0.8,
            AttrId.shield_kinetic_dmg_resonance: 0.6,
            AttrId.shield_explosive_dmg_resonance: 0.5}).id)
        fit.ship = item
        # Verification
        results = item.get_ehp(
            DmgProfile(em=25, thermal=6, kinetic=8.333, explosive=1))
        self.assertIsNone(results.hull)
        self.assertIsNone(results.armor)
        self.assertIsNone(results.shield)
        self.assertIsNone(results.total)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_resist_em(self):
        fit = Fit()
        item = Ship(self.ch.type(attrs={
            AttrId.hp: 10,
            AttrId.em_dmg_resonance: 0.9,
            AttrId.thermal_dmg_resonance: 0.8,
            AttrId.kinetic_dmg_resonance: 0.7,
            AttrId.explosive_dmg_resonance: 0.6,
            AttrId.armor_hp: 50,
            AttrId.armor_thermal_dmg_resonance: 0.6,
            AttrId.armor_kinetic_dmg_resonance: 0.8,
            AttrId.armor_explosive_dmg_resonance: 0.9,
            AttrId.shield_capacity: 600,
            AttrId.shield_em_dmg_resonance: 1.0,
            AttrId.shield_thermal_dmg_resonance: 0.8,
            AttrId.shield_kinetic_dmg_resonance: 0.6,
            AttrId.shield_explosive_dmg_resonance: 0.5}).id)
        fit.ship = item
        # Verification
        results = item.get_ehp(
            DmgProfile(em=25, thermal=6, kinetic=8.333, explosive=1))
        self.assertAlmostEqual(results.hull, 11.957, places=3)
        self.assertAlmostEqual(results.armor, 55.760, places=3)
        self.assertAlmostEqual(results.shield, 685.551, places=3)
        self.assertAlmostEqual(results.total, 753.267, places=3)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_resist_thermal(self):
        fit = Fit()
        item = Ship(self.ch.type(attrs={
            AttrId.hp: 10,
            AttrId.em_dmg_resonance: 0.9,
            AttrId.thermal_dmg_resonance: 0.8,
            AttrId.kinetic_dmg_resonance: 0.7,
            AttrId.explosive_dmg_resonance: 0.6,
            AttrId.armor_hp: 50,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_thermal_dmg_resonance: 0.6,
            AttrId.armor_kinetic_dmg_resonance: 0.8,
            AttrId.armor_explosive_dmg_resonance: 0.9,
            AttrId.shield_capacity: 600,
            AttrId.shield_em_dmg_resonance: 1.0,
            AttrId.shield_kinetic_dmg_resonance: 0.6,
            AttrId.shield_explosive_dmg_resonance: 0.5}).id)
        fit.ship = item
        # Verification
        results = item.get_ehp(
            DmgProfile(em=25, thermal=6, kinetic=8.333, explosive=1))
        self.assertAlmostEqual(results.hull, 11.957, places=3)
        self.assertAlmostEqual(results.armor, 95.276, places=3)
        self.assertAlmostEqual(results.shield, 663.012, places=3)
        self.assertAlmostEqual(results.total, 770.244, places=3)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_resist_kinetic(self):
        fit = Fit()
        item = Ship(self.ch.type(attrs={
            AttrId.hp: 10,
            AttrId.em_dmg_resonance: 0.9,
            AttrId.thermal_dmg_resonance: 0.8,
            AttrId.explosive_dmg_resonance: 0.6,
            AttrId.armor_hp: 50,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_thermal_dmg_resonance: 0.6,
            AttrId.armor_kinetic_dmg_resonance: 0.8,
            AttrId.armor_explosive_dmg_resonance: 0.9,
            AttrId.shield_capacity: 600,
            AttrId.shield_em_dmg_resonance: 1.0,
            AttrId.shield_thermal_dmg_resonance: 0.8,
            AttrId.shield_kinetic_dmg_resonance: 0.6,
            AttrId.shield_explosive_dmg_resonance: 0.5}).id)
        fit.ship = item
        # Verification
        results = item.get_ehp(
            DmgProfile(em=25, thermal=6, kinetic=8.333, explosive=1))
        self.assertAlmostEqual(results.hull, 11.132, places=3)
        self.assertAlmostEqual(results.armor, 95.276, places=3)
        self.assertAlmostEqual(results.shield, 685.551, places=3)
        self.assertAlmostEqual(results.total, 791.958, places=3)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_resist_explosive(self):
        fit = Fit()
        item = Ship(self.ch.type(attrs={
            AttrId.hp: 10,
            AttrId.em_dmg_resonance: 0.9,
            AttrId.thermal_dmg_resonance: 0.8,
            AttrId.kinetic_dmg_resonance: 0.7,
            AttrId.explosive_dmg_resonance: 0.6,
            AttrId.armor_hp: 50,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_thermal_dmg_resonance: 0.6,
            AttrId.armor_kinetic_dmg_resonance: 0.8,
            AttrId.shield_capacity: 600,
            AttrId.shield_em_dmg_resonance: 1.0,
            AttrId.shield_thermal_dmg_resonance: 0.8,
            AttrId.shield_kinetic_dmg_resonance: 0.6,
            AttrId.shield_explosive_dmg_resonance: 0.5}).id)
        fit.ship = item
        # Verification
        results = item.get_ehp(
            DmgProfile(em=25, thermal=6, kinetic=8.333, explosive=1))
        self.assertAlmostEqual(results.hull, 11.957, places=3)
        self.assertAlmostEqual(results.armor, 94.828, places=3)
        self.assertAlmostEqual(results.shield, 685.551, places=3)
        self.assertAlmostEqual(results.total, 792.335, places=3)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_resist_all(self):
        fit = Fit()
        item = Ship(self.ch.type(attrs={
            AttrId.hp: 10,
            AttrId.em_dmg_resonance: 0.9,
            AttrId.thermal_dmg_resonance: 0.8,
            AttrId.kinetic_dmg_resonance: 0.7,
            AttrId.explosive_dmg_resonance: 0.6,
            AttrId.armor_hp: 50,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_thermal_dmg_resonance: 0.6,
            AttrId.armor_kinetic_dmg_resonance: 0.8,
            AttrId.armor_explosive_dmg_resonance: 0.9,
            AttrId.shield_capacity: 600}).id)
        fit.ship = item
        # Verification
        results = item.get_ehp(
            DmgProfile(em=25, thermal=6, kinetic=8.333, explosive=1))
        self.assertAlmostEqual(results.hull, 11.957, places=3)
        self.assertAlmostEqual(results.armor, 95.276, places=3)
        self.assertAlmostEqual(results.shield, 600, places=3)
        self.assertAlmostEqual(results.total, 707.233, places=3)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_source(self):
        fit = Fit(source=None)
        item = Ship(self.ch.type(attrs={
            AttrId.hp: 1,
            AttrId.em_dmg_resonance: 0.8,
            AttrId.thermal_dmg_resonance: 0.8,
            AttrId.kinetic_dmg_resonance: 0.8,
            AttrId.explosive_dmg_resonance: 0.8,
            AttrId.armor_hp: 10,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_thermal_dmg_resonance: 0.4,
            AttrId.armor_kinetic_dmg_resonance: 0.4,
            AttrId.armor_explosive_dmg_resonance: 0.4,
            AttrId.shield_capacity: 100,
            AttrId.shield_em_dmg_resonance: 0.2,
            AttrId.shield_thermal_dmg_resonance: 0.2,
            AttrId.shield_kinetic_dmg_resonance: 0.2,
            AttrId.shield_explosive_dmg_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        results = item.get_ehp(
            DmgProfile(em=1, thermal=1, kinetic=1, explosive=1))
        self.assertIsNone(results.hull)
        self.assertIsNone(results.armor)
        self.assertIsNone(results.shield)
        self.assertIsNone(results.total)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)
