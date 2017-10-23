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
from tests.integration.item.item_testcase import ItemMixinTestCase


class TestItemMixinTankingWorstCaseEhp(ItemMixinTestCase):

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

    def test_equal(self):
        fit = Fit()
        item = Ship(self.ch.type(attributes={
            Attribute.hp: 1,
            Attribute.em_damage_resonance: 0.8,
            Attribute.thermal_damage_resonance: 0.8,
            Attribute.kinetic_damage_resonance: 0.8,
            Attribute.explosive_damage_resonance: 0.8,
            Attribute.armor_hp: 10,
            Attribute.armor_em_damage_resonance: 0.4,
            Attribute.armor_thermal_damage_resonance: 0.4,
            Attribute.armor_kinetic_damage_resonance: 0.4,
            Attribute.armor_explosive_damage_resonance: 0.4,
            Attribute.shield_capacity: 100,
            Attribute.shield_em_damage_resonance: 0.2,
            Attribute.shield_thermal_damage_resonance: 0.2,
            Attribute.shield_kinetic_damage_resonance: 0.2,
            Attribute.shield_explosive_damage_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 526.25)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_worst_em(self):
        fit = Fit()
        item = Ship(self.ch.type(attributes={
            Attribute.hp: 1,
            Attribute.em_damage_resonance: 0.8,
            Attribute.thermal_damage_resonance: 0.7,
            Attribute.kinetic_damage_resonance: 0.7,
            Attribute.explosive_damage_resonance: 0.7,
            Attribute.armor_hp: 10,
            Attribute.armor_em_damage_resonance: 0.4,
            Attribute.armor_thermal_damage_resonance: 0.3,
            Attribute.armor_kinetic_damage_resonance: 0.3,
            Attribute.armor_explosive_damage_resonance: 0.3,
            Attribute.shield_capacity: 100,
            Attribute.shield_em_damage_resonance: 0.2,
            Attribute.shield_thermal_damage_resonance: 0.1,
            Attribute.shield_kinetic_damage_resonance: 0.1,
            Attribute.shield_explosive_damage_resonance: 0.1}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 526.25)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_worst_thermal(self):
        fit = Fit()
        item = Ship(self.ch.type(attributes={
            Attribute.hp: 1,
            Attribute.em_damage_resonance: 0.7,
            Attribute.thermal_damage_resonance: 0.8,
            Attribute.kinetic_damage_resonance: 0.7,
            Attribute.explosive_damage_resonance: 0.7,
            Attribute.armor_hp: 10,
            Attribute.armor_em_damage_resonance: 0.3,
            Attribute.armor_thermal_damage_resonance: 0.4,
            Attribute.armor_kinetic_damage_resonance: 0.3,
            Attribute.armor_explosive_damage_resonance: 0.3,
            Attribute.shield_capacity: 100,
            Attribute.shield_em_damage_resonance: 0.1,
            Attribute.shield_thermal_damage_resonance: 0.2,
            Attribute.shield_kinetic_damage_resonance: 0.1,
            Attribute.shield_explosive_damage_resonance: 0.1}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 526.25)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_worst_kinetic(self):
        fit = Fit()
        item = Ship(self.ch.type(attributes={
            Attribute.hp: 1,
            Attribute.em_damage_resonance: 0.7,
            Attribute.thermal_damage_resonance: 0.7,
            Attribute.kinetic_damage_resonance: 0.8,
            Attribute.explosive_damage_resonance: 0.7,
            Attribute.armor_hp: 10,
            Attribute.armor_em_damage_resonance: 0.3,
            Attribute.armor_thermal_damage_resonance: 0.3,
            Attribute.armor_kinetic_damage_resonance: 0.4,
            Attribute.armor_explosive_damage_resonance: 0.3,
            Attribute.shield_capacity: 100,
            Attribute.shield_em_damage_resonance: 0.1,
            Attribute.shield_thermal_damage_resonance: 0.1,
            Attribute.shield_kinetic_damage_resonance: 0.2,
            Attribute.shield_explosive_damage_resonance: 0.1}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 526.25)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_worst_explosive(self):
        fit = Fit()
        item = Ship(self.ch.type(attributes={
            Attribute.hp: 1,
            Attribute.em_damage_resonance: 0.7,
            Attribute.thermal_damage_resonance: 0.7,
            Attribute.kinetic_damage_resonance: 0.7,
            Attribute.explosive_damage_resonance: 0.8,
            Attribute.armor_hp: 10,
            Attribute.armor_em_damage_resonance: 0.3,
            Attribute.armor_thermal_damage_resonance: 0.3,
            Attribute.armor_kinetic_damage_resonance: 0.3,
            Attribute.armor_explosive_damage_resonance: 0.4,
            Attribute.shield_capacity: 100,
            Attribute.shield_em_damage_resonance: 0.1,
            Attribute.shield_thermal_damage_resonance: 0.1,
            Attribute.shield_kinetic_damage_resonance: 0.1,
            Attribute.shield_explosive_damage_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 526.25)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_mixed(self):
        fit = Fit()
        item = Ship(self.ch.type(attributes={
            Attribute.hp: 1,
            Attribute.em_damage_resonance: 0.8,
            Attribute.thermal_damage_resonance: 0.7,
            Attribute.kinetic_damage_resonance: 0.7,
            Attribute.explosive_damage_resonance: 0.8,
            Attribute.armor_hp: 10,
            Attribute.armor_em_damage_resonance: 0.3,
            Attribute.armor_thermal_damage_resonance: 0.4,
            Attribute.armor_kinetic_damage_resonance: 0.4,
            Attribute.armor_explosive_damage_resonance: 0.3,
            Attribute.shield_capacity: 100,
            Attribute.shield_em_damage_resonance: 0.1,
            Attribute.shield_thermal_damage_resonance: 0.1,
            Attribute.shield_kinetic_damage_resonance: 0.2,
            Attribute.shield_explosive_damage_resonance: 0.01}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 526.25)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_hp_hull(self):
        fit = Fit()
        item = Ship(self.ch.type(attributes={
            Attribute.em_damage_resonance: 0.8,
            Attribute.thermal_damage_resonance: 0.8,
            Attribute.kinetic_damage_resonance: 0.8,
            Attribute.explosive_damage_resonance: 0.8,
            Attribute.armor_hp: 10,
            Attribute.armor_em_damage_resonance: 0.4,
            Attribute.armor_thermal_damage_resonance: 0.4,
            Attribute.armor_kinetic_damage_resonance: 0.4,
            Attribute.armor_explosive_damage_resonance: 0.4,
            Attribute.shield_capacity: 100,
            Attribute.shield_em_damage_resonance: 0.2,
            Attribute.shield_thermal_damage_resonance: 0.2,
            Attribute.shield_kinetic_damage_resonance: 0.2,
            Attribute.shield_explosive_damage_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertIsNone(item.worst_case_ehp.hull)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 525)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_hp_armor(self):
        fit = Fit()
        item = Ship(self.ch.type(attributes={
            Attribute.hp: 1,
            Attribute.em_damage_resonance: 0.8,
            Attribute.thermal_damage_resonance: 0.8,
            Attribute.kinetic_damage_resonance: 0.8,
            Attribute.explosive_damage_resonance: 0.8,
            Attribute.armor_em_damage_resonance: 0.4,
            Attribute.armor_thermal_damage_resonance: 0.4,
            Attribute.armor_kinetic_damage_resonance: 0.4,
            Attribute.armor_explosive_damage_resonance: 0.4,
            Attribute.shield_capacity: 100,
            Attribute.shield_em_damage_resonance: 0.2,
            Attribute.shield_thermal_damage_resonance: 0.2,
            Attribute.shield_kinetic_damage_resonance: 0.2,
            Attribute.shield_explosive_damage_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertIsNone(item.worst_case_ehp.armor)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 501.25)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_hp_shield(self):
        fit = Fit()
        item = Ship(self.ch.type(attributes={
            Attribute.hp: 1,
            Attribute.em_damage_resonance: 0.8,
            Attribute.thermal_damage_resonance: 0.8,
            Attribute.kinetic_damage_resonance: 0.8,
            Attribute.explosive_damage_resonance: 0.8,
            Attribute.armor_hp: 10,
            Attribute.armor_em_damage_resonance: 0.4,
            Attribute.armor_thermal_damage_resonance: 0.4,
            Attribute.armor_kinetic_damage_resonance: 0.4,
            Attribute.armor_explosive_damage_resonance: 0.4,
            Attribute.shield_em_damage_resonance: 0.2,
            Attribute.shield_thermal_damage_resonance: 0.2,
            Attribute.shield_kinetic_damage_resonance: 0.2,
            Attribute.shield_explosive_damage_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertIsNone(item.worst_case_ehp.shield)
        self.assertAlmostEqual(item.worst_case_ehp.total, 26.25)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_hp_all(self):
        fit = Fit()
        item = Ship(self.ch.type(attributes={
            Attribute.em_damage_resonance: 0.8,
            Attribute.thermal_damage_resonance: 0.8,
            Attribute.kinetic_damage_resonance: 0.8,
            Attribute.explosive_damage_resonance: 0.8,
            Attribute.armor_em_damage_resonance: 0.4,
            Attribute.armor_thermal_damage_resonance: 0.4,
            Attribute.armor_kinetic_damage_resonance: 0.4,
            Attribute.armor_explosive_damage_resonance: 0.4,
            Attribute.shield_em_damage_resonance: 0.2,
            Attribute.shield_thermal_damage_resonance: 0.2,
            Attribute.shield_kinetic_damage_resonance: 0.2,
            Attribute.shield_explosive_damage_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertIsNone(item.worst_case_ehp.hull)
        self.assertIsNone(item.worst_case_ehp.armor)
        self.assertIsNone(item.worst_case_ehp.shield)
        self.assertIsNone(item.worst_case_ehp.total)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_resistance_em(self):
        fit = Fit()
        item = Ship(self.ch.type(attributes={
            Attribute.hp: 1,
            Attribute.thermal_damage_resonance: 0.8,
            Attribute.kinetic_damage_resonance: 0.8,
            Attribute.explosive_damage_resonance: 0.8,
            Attribute.armor_hp: 10,
            Attribute.armor_em_damage_resonance: 0.4,
            Attribute.armor_thermal_damage_resonance: 0.4,
            Attribute.armor_kinetic_damage_resonance: 0.4,
            Attribute.armor_explosive_damage_resonance: 0.4,
            Attribute.shield_capacity: 100,
            Attribute.shield_em_damage_resonance: 0.2,
            Attribute.shield_thermal_damage_resonance: 0.2,
            Attribute.shield_kinetic_damage_resonance: 0.2,
            Attribute.shield_explosive_damage_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 526)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_resistance_thermal(self):
        fit = Fit()
        item = Ship(self.ch.type(attributes={
            Attribute.hp: 1,
            Attribute.em_damage_resonance: 0.8,
            Attribute.thermal_damage_resonance: 0.8,
            Attribute.kinetic_damage_resonance: 0.8,
            Attribute.explosive_damage_resonance: 0.8,
            Attribute.armor_hp: 10,
            Attribute.armor_em_damage_resonance: 0.4,
            Attribute.armor_kinetic_damage_resonance: 0.4,
            Attribute.armor_explosive_damage_resonance: 0.4,
            Attribute.shield_capacity: 100,
            Attribute.shield_em_damage_resonance: 0.2,
            Attribute.shield_thermal_damage_resonance: 0.2,
            Attribute.shield_kinetic_damage_resonance: 0.2,
            Attribute.shield_explosive_damage_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 10)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 511.25)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_resistance_kinetic(self):
        fit = Fit()
        item = Ship(self.ch.type(attributes={
            Attribute.hp: 1,
            Attribute.em_damage_resonance: 0.8,
            Attribute.thermal_damage_resonance: 0.8,
            Attribute.kinetic_damage_resonance: 0.8,
            Attribute.explosive_damage_resonance: 0.8,
            Attribute.armor_hp: 10,
            Attribute.armor_em_damage_resonance: 0.4,
            Attribute.armor_thermal_damage_resonance: 0.4,
            Attribute.armor_kinetic_damage_resonance: 0.4,
            Attribute.armor_explosive_damage_resonance: 0.4,
            Attribute.shield_capacity: 100,
            Attribute.shield_em_damage_resonance: 0.2,
            Attribute.shield_thermal_damage_resonance: 0.2,
            Attribute.shield_explosive_damage_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 100)
        self.assertAlmostEqual(item.worst_case_ehp.total, 126.25)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_resistance_explosive(self):
        fit = Fit()
        item = Ship(self.ch.type(attributes={
            Attribute.hp: 1,
            Attribute.em_damage_resonance: 0.8,
            Attribute.thermal_damage_resonance: 0.8,
            Attribute.kinetic_damage_resonance: 0.8,
            Attribute.explosive_damage_resonance: 0.8,
            Attribute.armor_hp: 10,
            Attribute.armor_em_damage_resonance: 0.4,
            Attribute.armor_thermal_damage_resonance: 0.4,
            Attribute.armor_kinetic_damage_resonance: 0.4,
            Attribute.shield_capacity: 100,
            Attribute.shield_em_damage_resonance: 0.2,
            Attribute.shield_thermal_damage_resonance: 0.2,
            Attribute.shield_kinetic_damage_resonance: 0.2,
            Attribute.shield_explosive_damage_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 10)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 511.25)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_resistance_all(self):
        fit = Fit()
        item = Ship(self.ch.type(attributes={
            Attribute.hp: 1,
            Attribute.em_damage_resonance: 0.8,
            Attribute.thermal_damage_resonance: 0.8,
            Attribute.kinetic_damage_resonance: 0.8,
            Attribute.explosive_damage_resonance: 0.8,
            Attribute.armor_hp: 10,
            Attribute.armor_em_damage_resonance: 0.4,
            Attribute.armor_thermal_damage_resonance: 0.4,
            Attribute.armor_kinetic_damage_resonance: 0.4,
            Attribute.armor_explosive_damage_resonance: 0.4,
            Attribute.shield_capacity: 100}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 100)
        self.assertAlmostEqual(item.worst_case_ehp.total, 126.25)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_source(self):
        fit = Fit(source=None)
        item = Ship(self.ch.type(attributes={
            Attribute.hp: 1,
            Attribute.em_damage_resonance: 0.8,
            Attribute.thermal_damage_resonance: 0.8,
            Attribute.kinetic_damage_resonance: 0.8,
            Attribute.explosive_damage_resonance: 0.8,
            Attribute.armor_hp: 10,
            Attribute.armor_em_damage_resonance: 0.4,
            Attribute.armor_thermal_damage_resonance: 0.4,
            Attribute.armor_kinetic_damage_resonance: 0.4,
            Attribute.armor_explosive_damage_resonance: 0.4,
            Attribute.shield_capacity: 100,
            Attribute.shield_em_damage_resonance: 0.2,
            Attribute.shield_thermal_damage_resonance: 0.2,
            Attribute.shield_kinetic_damage_resonance: 0.2,
            Attribute.shield_explosive_damage_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertIsNone(item.worst_case_ehp.hull)
        self.assertIsNone(item.worst_case_ehp.armor)
        self.assertIsNone(item.worst_case_ehp.shield)
        self.assertIsNone(item.worst_case_ehp.total)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)
