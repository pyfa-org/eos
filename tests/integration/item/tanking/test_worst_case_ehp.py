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
from tests.integration.item.item_testcase import ItemMixinTestCase


class TestItemMixinTankingWorstCaseEhp(ItemMixinTestCase):

    def setUp(self):
        super().setUp()
        self.ch.attribute(attribute_id=AttributeId.hp)
        self.ch.attribute(attribute_id=AttributeId.em_damage_resonance)
        self.ch.attribute(attribute_id=AttributeId.thermal_damage_resonance)
        self.ch.attribute(attribute_id=AttributeId.kinetic_damage_resonance)
        self.ch.attribute(attribute_id=AttributeId.explosive_damage_resonance)
        self.ch.attribute(attribute_id=AttributeId.armor_hp)
        self.ch.attribute(attribute_id=AttributeId.armor_em_damage_resonance)
        self.ch.attribute(
            attribute_id=AttributeId.armor_thermal_damage_resonance)
        self.ch.attribute(
            attribute_id=AttributeId.armor_kinetic_damage_resonance)
        self.ch.attribute(
            attribute_id=AttributeId.armor_explosive_damage_resonance)
        self.ch.attribute(attribute_id=AttributeId.shield_capacity)
        self.ch.attribute(attribute_id=AttributeId.shield_em_damage_resonance)
        self.ch.attribute(
            attribute_id=AttributeId.shield_thermal_damage_resonance)
        self.ch.attribute(
            attribute_id=AttributeId.shield_kinetic_damage_resonance)
        self.ch.attribute(
            attribute_id=AttributeId.shield_explosive_damage_resonance)

    def test_equal(self):
        fit = Fit()
        item = Ship(self.ch.type(
            attributes={
                AttributeId.hp: 1,
                AttributeId.em_damage_resonance: 0.8,
                AttributeId.thermal_damage_resonance: 0.8,
                AttributeId.kinetic_damage_resonance: 0.8,
                AttributeId.explosive_damage_resonance: 0.8,
                AttributeId.armor_hp: 10,
                AttributeId.armor_em_damage_resonance: 0.4,
                AttributeId.armor_thermal_damage_resonance: 0.4,
                AttributeId.armor_kinetic_damage_resonance: 0.4,
                AttributeId.armor_explosive_damage_resonance: 0.4,
                AttributeId.shield_capacity: 100,
                AttributeId.shield_em_damage_resonance: 0.2,
                AttributeId.shield_thermal_damage_resonance: 0.2,
                AttributeId.shield_kinetic_damage_resonance: 0.2,
                AttributeId.shield_explosive_damage_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 526.25)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_worst_em(self):
        fit = Fit()
        item = Ship(self.ch.type(
            attributes={
                AttributeId.hp: 1,
                AttributeId.em_damage_resonance: 0.8,
                AttributeId.thermal_damage_resonance: 0.7,
                AttributeId.kinetic_damage_resonance: 0.7,
                AttributeId.explosive_damage_resonance: 0.7,
                AttributeId.armor_hp: 10,
                AttributeId.armor_em_damage_resonance: 0.4,
                AttributeId.armor_thermal_damage_resonance: 0.3,
                AttributeId.armor_kinetic_damage_resonance: 0.3,
                AttributeId.armor_explosive_damage_resonance: 0.3,
                AttributeId.shield_capacity: 100,
                AttributeId.shield_em_damage_resonance: 0.2,
                AttributeId.shield_thermal_damage_resonance: 0.1,
                AttributeId.shield_kinetic_damage_resonance: 0.1,
                AttributeId.shield_explosive_damage_resonance: 0.1}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 526.25)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_worst_thermal(self):
        fit = Fit()
        item = Ship(self.ch.type(
            attributes={
                AttributeId.hp: 1,
                AttributeId.em_damage_resonance: 0.7,
                AttributeId.thermal_damage_resonance: 0.8,
                AttributeId.kinetic_damage_resonance: 0.7,
                AttributeId.explosive_damage_resonance: 0.7,
                AttributeId.armor_hp: 10,
                AttributeId.armor_em_damage_resonance: 0.3,
                AttributeId.armor_thermal_damage_resonance: 0.4,
                AttributeId.armor_kinetic_damage_resonance: 0.3,
                AttributeId.armor_explosive_damage_resonance: 0.3,
                AttributeId.shield_capacity: 100,
                AttributeId.shield_em_damage_resonance: 0.1,
                AttributeId.shield_thermal_damage_resonance: 0.2,
                AttributeId.shield_kinetic_damage_resonance: 0.1,
                AttributeId.shield_explosive_damage_resonance: 0.1}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 526.25)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_worst_kinetic(self):
        fit = Fit()
        item = Ship(self.ch.type(
            attributes={
                AttributeId.hp: 1,
                AttributeId.em_damage_resonance: 0.7,
                AttributeId.thermal_damage_resonance: 0.7,
                AttributeId.kinetic_damage_resonance: 0.8,
                AttributeId.explosive_damage_resonance: 0.7,
                AttributeId.armor_hp: 10,
                AttributeId.armor_em_damage_resonance: 0.3,
                AttributeId.armor_thermal_damage_resonance: 0.3,
                AttributeId.armor_kinetic_damage_resonance: 0.4,
                AttributeId.armor_explosive_damage_resonance: 0.3,
                AttributeId.shield_capacity: 100,
                AttributeId.shield_em_damage_resonance: 0.1,
                AttributeId.shield_thermal_damage_resonance: 0.1,
                AttributeId.shield_kinetic_damage_resonance: 0.2,
                AttributeId.shield_explosive_damage_resonance: 0.1}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 526.25)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_worst_explosive(self):
        fit = Fit()
        item = Ship(self.ch.type(
            attributes={
                AttributeId.hp: 1,
                AttributeId.em_damage_resonance: 0.7,
                AttributeId.thermal_damage_resonance: 0.7,
                AttributeId.kinetic_damage_resonance: 0.7,
                AttributeId.explosive_damage_resonance: 0.8,
                AttributeId.armor_hp: 10,
                AttributeId.armor_em_damage_resonance: 0.3,
                AttributeId.armor_thermal_damage_resonance: 0.3,
                AttributeId.armor_kinetic_damage_resonance: 0.3,
                AttributeId.armor_explosive_damage_resonance: 0.4,
                AttributeId.shield_capacity: 100,
                AttributeId.shield_em_damage_resonance: 0.1,
                AttributeId.shield_thermal_damage_resonance: 0.1,
                AttributeId.shield_kinetic_damage_resonance: 0.1,
                AttributeId.shield_explosive_damage_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 526.25)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_mixed(self):
        fit = Fit()
        item = Ship(self.ch.type(
            attributes={
                AttributeId.hp: 1,
                AttributeId.em_damage_resonance: 0.8,
                AttributeId.thermal_damage_resonance: 0.7,
                AttributeId.kinetic_damage_resonance: 0.7,
                AttributeId.explosive_damage_resonance: 0.8,
                AttributeId.armor_hp: 10,
                AttributeId.armor_em_damage_resonance: 0.3,
                AttributeId.armor_thermal_damage_resonance: 0.4,
                AttributeId.armor_kinetic_damage_resonance: 0.4,
                AttributeId.armor_explosive_damage_resonance: 0.3,
                AttributeId.shield_capacity: 100,
                AttributeId.shield_em_damage_resonance: 0.1,
                AttributeId.shield_thermal_damage_resonance: 0.1,
                AttributeId.shield_kinetic_damage_resonance: 0.2,
                AttributeId.shield_explosive_damage_resonance: 0.01}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 526.25)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_none_hp_hull(self):
        fit = Fit()
        item = Ship(self.ch.type(
            attributes={
                AttributeId.em_damage_resonance: 0.8,
                AttributeId.thermal_damage_resonance: 0.8,
                AttributeId.kinetic_damage_resonance: 0.8,
                AttributeId.explosive_damage_resonance: 0.8,
                AttributeId.armor_hp: 10,
                AttributeId.armor_em_damage_resonance: 0.4,
                AttributeId.armor_thermal_damage_resonance: 0.4,
                AttributeId.armor_kinetic_damage_resonance: 0.4,
                AttributeId.armor_explosive_damage_resonance: 0.4,
                AttributeId.shield_capacity: 100,
                AttributeId.shield_em_damage_resonance: 0.2,
                AttributeId.shield_thermal_damage_resonance: 0.2,
                AttributeId.shield_kinetic_damage_resonance: 0.2,
                AttributeId.shield_explosive_damage_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertIsNone(item.worst_case_ehp.hull)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 525)
        # Cleanup
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_none_hp_armor(self):
        fit = Fit()
        item = Ship(self.ch.type(
            attributes={
                AttributeId.hp: 1,
                AttributeId.em_damage_resonance: 0.8,
                AttributeId.thermal_damage_resonance: 0.8,
                AttributeId.kinetic_damage_resonance: 0.8,
                AttributeId.explosive_damage_resonance: 0.8,
                AttributeId.armor_em_damage_resonance: 0.4,
                AttributeId.armor_thermal_damage_resonance: 0.4,
                AttributeId.armor_kinetic_damage_resonance: 0.4,
                AttributeId.armor_explosive_damage_resonance: 0.4,
                AttributeId.shield_capacity: 100,
                AttributeId.shield_em_damage_resonance: 0.2,
                AttributeId.shield_thermal_damage_resonance: 0.2,
                AttributeId.shield_kinetic_damage_resonance: 0.2,
                AttributeId.shield_explosive_damage_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertIsNone(item.worst_case_ehp.armor)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 501.25)
        # Cleanup
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_none_hp_shield(self):
        fit = Fit()
        item = Ship(self.ch.type(
            attributes={
                AttributeId.hp: 1,
                AttributeId.em_damage_resonance: 0.8,
                AttributeId.thermal_damage_resonance: 0.8,
                AttributeId.kinetic_damage_resonance: 0.8,
                AttributeId.explosive_damage_resonance: 0.8,
                AttributeId.armor_hp: 10,
                AttributeId.armor_em_damage_resonance: 0.4,
                AttributeId.armor_thermal_damage_resonance: 0.4,
                AttributeId.armor_kinetic_damage_resonance: 0.4,
                AttributeId.armor_explosive_damage_resonance: 0.4,
                AttributeId.shield_em_damage_resonance: 0.2,
                AttributeId.shield_thermal_damage_resonance: 0.2,
                AttributeId.shield_kinetic_damage_resonance: 0.2,
                AttributeId.shield_explosive_damage_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertIsNone(item.worst_case_ehp.shield)
        self.assertAlmostEqual(item.worst_case_ehp.total, 26.25)
        # Cleanup
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_none_hp_all(self):
        fit = Fit()
        item = Ship(self.ch.type(
            attributes={
                AttributeId.em_damage_resonance: 0.8,
                AttributeId.thermal_damage_resonance: 0.8,
                AttributeId.kinetic_damage_resonance: 0.8,
                AttributeId.explosive_damage_resonance: 0.8,
                AttributeId.armor_em_damage_resonance: 0.4,
                AttributeId.armor_thermal_damage_resonance: 0.4,
                AttributeId.armor_kinetic_damage_resonance: 0.4,
                AttributeId.armor_explosive_damage_resonance: 0.4,
                AttributeId.shield_em_damage_resonance: 0.2,
                AttributeId.shield_thermal_damage_resonance: 0.2,
                AttributeId.shield_kinetic_damage_resonance: 0.2,
                AttributeId.shield_explosive_damage_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertIsNone(item.worst_case_ehp.hull)
        self.assertIsNone(item.worst_case_ehp.armor)
        self.assertIsNone(item.worst_case_ehp.shield)
        self.assertIsNone(item.worst_case_ehp.total)
        # Cleanup
        self.assertEqual(len(self.log), 3)
        self.assert_fit_buffers_empty(fit)

    def test_none_resistance_em(self):
        fit = Fit()
        item = Ship(self.ch.type(
            attributes={
                AttributeId.hp: 1,
                AttributeId.thermal_damage_resonance: 0.8,
                AttributeId.kinetic_damage_resonance: 0.8,
                AttributeId.explosive_damage_resonance: 0.8,
                AttributeId.armor_hp: 10,
                AttributeId.armor_em_damage_resonance: 0.4,
                AttributeId.armor_thermal_damage_resonance: 0.4,
                AttributeId.armor_kinetic_damage_resonance: 0.4,
                AttributeId.armor_explosive_damage_resonance: 0.4,
                AttributeId.shield_capacity: 100,
                AttributeId.shield_em_damage_resonance: 0.2,
                AttributeId.shield_thermal_damage_resonance: 0.2,
                AttributeId.shield_kinetic_damage_resonance: 0.2,
                AttributeId.shield_explosive_damage_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 526)
        # Cleanup
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_none_resistance_thermal(self):
        fit = Fit()
        item = Ship(self.ch.type(
            attributes={
                AttributeId.hp: 1,
                AttributeId.em_damage_resonance: 0.8,
                AttributeId.thermal_damage_resonance: 0.8,
                AttributeId.kinetic_damage_resonance: 0.8,
                AttributeId.explosive_damage_resonance: 0.8,
                AttributeId.armor_hp: 10,
                AttributeId.armor_em_damage_resonance: 0.4,
                AttributeId.armor_kinetic_damage_resonance: 0.4,
                AttributeId.armor_explosive_damage_resonance: 0.4,
                AttributeId.shield_capacity: 100,
                AttributeId.shield_em_damage_resonance: 0.2,
                AttributeId.shield_thermal_damage_resonance: 0.2,
                AttributeId.shield_kinetic_damage_resonance: 0.2,
                AttributeId.shield_explosive_damage_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 10)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 511.25)
        # Cleanup
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_none_resistance_kinetic(self):
        fit = Fit()
        item = Ship(self.ch.type(
            attributes={
                AttributeId.hp: 1,
                AttributeId.em_damage_resonance: 0.8,
                AttributeId.thermal_damage_resonance: 0.8,
                AttributeId.kinetic_damage_resonance: 0.8,
                AttributeId.explosive_damage_resonance: 0.8,
                AttributeId.armor_hp: 10,
                AttributeId.armor_em_damage_resonance: 0.4,
                AttributeId.armor_thermal_damage_resonance: 0.4,
                AttributeId.armor_kinetic_damage_resonance: 0.4,
                AttributeId.armor_explosive_damage_resonance: 0.4,
                AttributeId.shield_capacity: 100,
                AttributeId.shield_em_damage_resonance: 0.2,
                AttributeId.shield_thermal_damage_resonance: 0.2,
                AttributeId.shield_explosive_damage_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 100)
        self.assertAlmostEqual(item.worst_case_ehp.total, 126.25)
        # Cleanup
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_none_resistance_explosive(self):
        fit = Fit()
        item = Ship(self.ch.type(
            attributes={
                AttributeId.hp: 1,
                AttributeId.em_damage_resonance: 0.8,
                AttributeId.thermal_damage_resonance: 0.8,
                AttributeId.kinetic_damage_resonance: 0.8,
                AttributeId.explosive_damage_resonance: 0.8,
                AttributeId.armor_hp: 10,
                AttributeId.armor_em_damage_resonance: 0.4,
                AttributeId.armor_thermal_damage_resonance: 0.4,
                AttributeId.armor_kinetic_damage_resonance: 0.4,
                AttributeId.shield_capacity: 100,
                AttributeId.shield_em_damage_resonance: 0.2,
                AttributeId.shield_thermal_damage_resonance: 0.2,
                AttributeId.shield_kinetic_damage_resonance: 0.2,
                AttributeId.shield_explosive_damage_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 10)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 511.25)
        # Cleanup
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_none_resistance_all(self):
        fit = Fit()
        item = Ship(self.ch.type(
            attributes={
                AttributeId.hp: 1,
                AttributeId.em_damage_resonance: 0.8,
                AttributeId.thermal_damage_resonance: 0.8,
                AttributeId.kinetic_damage_resonance: 0.8,
                AttributeId.explosive_damage_resonance: 0.8,
                AttributeId.armor_hp: 10,
                AttributeId.armor_em_damage_resonance: 0.4,
                AttributeId.armor_thermal_damage_resonance: 0.4,
                AttributeId.armor_kinetic_damage_resonance: 0.4,
                AttributeId.armor_explosive_damage_resonance: 0.4,
                AttributeId.shield_capacity: 100}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 100)
        self.assertAlmostEqual(item.worst_case_ehp.total, 126.25)
        # Cleanup
        self.assertEqual(len(self.log), 4)
        self.assert_fit_buffers_empty(fit)

    def test_no_source(self):
        fit = Fit(source=None)
        item = Ship(self.ch.type(
            attributes={
                AttributeId.hp: 1,
                AttributeId.em_damage_resonance: 0.8,
                AttributeId.thermal_damage_resonance: 0.8,
                AttributeId.kinetic_damage_resonance: 0.8,
                AttributeId.explosive_damage_resonance: 0.8,
                AttributeId.armor_hp: 10,
                AttributeId.armor_em_damage_resonance: 0.4,
                AttributeId.armor_thermal_damage_resonance: 0.4,
                AttributeId.armor_kinetic_damage_resonance: 0.4,
                AttributeId.armor_explosive_damage_resonance: 0.4,
                AttributeId.shield_capacity: 100,
                AttributeId.shield_em_damage_resonance: 0.2,
                AttributeId.shield_thermal_damage_resonance: 0.2,
                AttributeId.shield_kinetic_damage_resonance: 0.2,
                AttributeId.shield_explosive_damage_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertIsNone(item.worst_case_ehp.hull)
        self.assertIsNone(item.worst_case_ehp.armor)
        self.assertIsNone(item.worst_case_ehp.shield)
        self.assertIsNone(item.worst_case_ehp.total)
        # Cleanup
        self.assertEqual(len(self.log), 15)
        self.assert_fit_buffers_empty(fit)
