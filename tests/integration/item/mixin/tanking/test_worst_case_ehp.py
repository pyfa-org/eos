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


from eos import Fit
from eos import Ship
from eos.const.eve import AttrId
from tests.integration.item.testcase import ItemMixinTestCase


class TestItemMixinTankingWorstCaseEhp(ItemMixinTestCase):

    def setUp(self):
        ItemMixinTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.hp)
        self.mkattr(attr_id=AttrId.em_dmg_resonance)
        self.mkattr(attr_id=AttrId.thermal_dmg_resonance)
        self.mkattr(attr_id=AttrId.kinetic_dmg_resonance)
        self.mkattr(attr_id=AttrId.explosive_dmg_resonance)
        self.mkattr(attr_id=AttrId.armor_hp)
        self.mkattr(attr_id=AttrId.armor_em_dmg_resonance)
        self.mkattr(attr_id=AttrId.armor_thermal_dmg_resonance)
        self.mkattr(attr_id=AttrId.armor_kinetic_dmg_resonance)
        self.mkattr(attr_id=AttrId.armor_explosive_dmg_resonance)
        self.mkattr(attr_id=AttrId.shield_capacity)
        self.mkattr(attr_id=AttrId.shield_em_dmg_resonance)
        self.mkattr(attr_id=AttrId.shield_thermal_dmg_resonance)
        self.mkattr(attr_id=AttrId.shield_kinetic_dmg_resonance)
        self.mkattr(attr_id=AttrId.shield_explosive_dmg_resonance)

    def test_equal(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
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
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 526.25)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_worst_em(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
            AttrId.hp: 1,
            AttrId.em_dmg_resonance: 0.8,
            AttrId.thermal_dmg_resonance: 0.7,
            AttrId.kinetic_dmg_resonance: 0.7,
            AttrId.explosive_dmg_resonance: 0.7,
            AttrId.armor_hp: 10,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_thermal_dmg_resonance: 0.3,
            AttrId.armor_kinetic_dmg_resonance: 0.3,
            AttrId.armor_explosive_dmg_resonance: 0.3,
            AttrId.shield_capacity: 100,
            AttrId.shield_em_dmg_resonance: 0.2,
            AttrId.shield_thermal_dmg_resonance: 0.1,
            AttrId.shield_kinetic_dmg_resonance: 0.1,
            AttrId.shield_explosive_dmg_resonance: 0.1}).id)
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
        item = Ship(self.mktype(attrs={
            AttrId.hp: 1,
            AttrId.em_dmg_resonance: 0.7,
            AttrId.thermal_dmg_resonance: 0.8,
            AttrId.kinetic_dmg_resonance: 0.7,
            AttrId.explosive_dmg_resonance: 0.7,
            AttrId.armor_hp: 10,
            AttrId.armor_em_dmg_resonance: 0.3,
            AttrId.armor_thermal_dmg_resonance: 0.4,
            AttrId.armor_kinetic_dmg_resonance: 0.3,
            AttrId.armor_explosive_dmg_resonance: 0.3,
            AttrId.shield_capacity: 100,
            AttrId.shield_em_dmg_resonance: 0.1,
            AttrId.shield_thermal_dmg_resonance: 0.2,
            AttrId.shield_kinetic_dmg_resonance: 0.1,
            AttrId.shield_explosive_dmg_resonance: 0.1}).id)
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
        item = Ship(self.mktype(attrs={
            AttrId.hp: 1,
            AttrId.em_dmg_resonance: 0.7,
            AttrId.thermal_dmg_resonance: 0.7,
            AttrId.kinetic_dmg_resonance: 0.8,
            AttrId.explosive_dmg_resonance: 0.7,
            AttrId.armor_hp: 10,
            AttrId.armor_em_dmg_resonance: 0.3,
            AttrId.armor_thermal_dmg_resonance: 0.3,
            AttrId.armor_kinetic_dmg_resonance: 0.4,
            AttrId.armor_explosive_dmg_resonance: 0.3,
            AttrId.shield_capacity: 100,
            AttrId.shield_em_dmg_resonance: 0.1,
            AttrId.shield_thermal_dmg_resonance: 0.1,
            AttrId.shield_kinetic_dmg_resonance: 0.2,
            AttrId.shield_explosive_dmg_resonance: 0.1}).id)
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
        item = Ship(self.mktype(attrs={
            AttrId.hp: 1,
            AttrId.em_dmg_resonance: 0.7,
            AttrId.thermal_dmg_resonance: 0.7,
            AttrId.kinetic_dmg_resonance: 0.7,
            AttrId.explosive_dmg_resonance: 0.8,
            AttrId.armor_hp: 10,
            AttrId.armor_em_dmg_resonance: 0.3,
            AttrId.armor_thermal_dmg_resonance: 0.3,
            AttrId.armor_kinetic_dmg_resonance: 0.3,
            AttrId.armor_explosive_dmg_resonance: 0.4,
            AttrId.shield_capacity: 100,
            AttrId.shield_em_dmg_resonance: 0.1,
            AttrId.shield_thermal_dmg_resonance: 0.1,
            AttrId.shield_kinetic_dmg_resonance: 0.1,
            AttrId.shield_explosive_dmg_resonance: 0.2}).id)
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
        item = Ship(self.mktype(attrs={
            AttrId.hp: 1,
            AttrId.em_dmg_resonance: 0.8,
            AttrId.thermal_dmg_resonance: 0.7,
            AttrId.kinetic_dmg_resonance: 0.7,
            AttrId.explosive_dmg_resonance: 0.8,
            AttrId.armor_hp: 10,
            AttrId.armor_em_dmg_resonance: 0.3,
            AttrId.armor_thermal_dmg_resonance: 0.4,
            AttrId.armor_kinetic_dmg_resonance: 0.4,
            AttrId.armor_explosive_dmg_resonance: 0.3,
            AttrId.shield_capacity: 100,
            AttrId.shield_em_dmg_resonance: 0.1,
            AttrId.shield_thermal_dmg_resonance: 0.1,
            AttrId.shield_kinetic_dmg_resonance: 0.2,
            AttrId.shield_explosive_dmg_resonance: 0.01}).id)
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
        item = Ship(self.mktype(attrs={
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
        self.assertIsNone(item.worst_case_ehp.hull)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 525)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_hp_armor(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
            AttrId.hp: 1,
            AttrId.em_dmg_resonance: 0.8,
            AttrId.thermal_dmg_resonance: 0.8,
            AttrId.kinetic_dmg_resonance: 0.8,
            AttrId.explosive_dmg_resonance: 0.8,
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
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertIsNone(item.worst_case_ehp.armor)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 501.25)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_hp_shield(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
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
            AttrId.shield_em_dmg_resonance: 0.2,
            AttrId.shield_thermal_dmg_resonance: 0.2,
            AttrId.shield_kinetic_dmg_resonance: 0.2,
            AttrId.shield_explosive_dmg_resonance: 0.2}).id)
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
        item = Ship(self.mktype(attrs={
            AttrId.em_dmg_resonance: 0.8,
            AttrId.thermal_dmg_resonance: 0.8,
            AttrId.kinetic_dmg_resonance: 0.8,
            AttrId.explosive_dmg_resonance: 0.8,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_thermal_dmg_resonance: 0.4,
            AttrId.armor_kinetic_dmg_resonance: 0.4,
            AttrId.armor_explosive_dmg_resonance: 0.4,
            AttrId.shield_em_dmg_resonance: 0.2,
            AttrId.shield_thermal_dmg_resonance: 0.2,
            AttrId.shield_kinetic_dmg_resonance: 0.2,
            AttrId.shield_explosive_dmg_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertIsNone(item.worst_case_ehp.hull)
        self.assertIsNone(item.worst_case_ehp.armor)
        self.assertIsNone(item.worst_case_ehp.shield)
        self.assertIsNone(item.worst_case_ehp.total)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_resist_em(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
            AttrId.hp: 1,
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
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 526)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_resist_thermal(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
            AttrId.hp: 1,
            AttrId.em_dmg_resonance: 0.8,
            AttrId.thermal_dmg_resonance: 0.8,
            AttrId.kinetic_dmg_resonance: 0.8,
            AttrId.explosive_dmg_resonance: 0.8,
            AttrId.armor_hp: 10,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_kinetic_dmg_resonance: 0.4,
            AttrId.armor_explosive_dmg_resonance: 0.4,
            AttrId.shield_capacity: 100,
            AttrId.shield_em_dmg_resonance: 0.2,
            AttrId.shield_thermal_dmg_resonance: 0.2,
            AttrId.shield_kinetic_dmg_resonance: 0.2,
            AttrId.shield_explosive_dmg_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 10)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 511.25)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_resist_kinetic(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
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
            AttrId.shield_explosive_dmg_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 100)
        self.assertAlmostEqual(item.worst_case_ehp.total, 126.25)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_resist_explosive(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
            AttrId.hp: 1,
            AttrId.em_dmg_resonance: 0.8,
            AttrId.thermal_dmg_resonance: 0.8,
            AttrId.kinetic_dmg_resonance: 0.8,
            AttrId.explosive_dmg_resonance: 0.8,
            AttrId.armor_hp: 10,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_thermal_dmg_resonance: 0.4,
            AttrId.armor_kinetic_dmg_resonance: 0.4,
            AttrId.shield_capacity: 100,
            AttrId.shield_em_dmg_resonance: 0.2,
            AttrId.shield_thermal_dmg_resonance: 0.2,
            AttrId.shield_kinetic_dmg_resonance: 0.2,
            AttrId.shield_explosive_dmg_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 10)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 511.25)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_resist_all(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
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
            AttrId.shield_capacity: 100}).id)
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
        item = Ship(self.mktype(attrs={
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
        self.assertIsNone(item.worst_case_ehp.hull)
        self.assertIsNone(item.worst_case_ehp.armor)
        self.assertIsNone(item.worst_case_ehp.shield)
        self.assertIsNone(item.worst_case_ehp.total)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)
