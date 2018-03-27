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


from eos import DmgProfile
from eos import Fit
from eos import Ship
from eos.const.eve import AttrId
from tests.integration.item.testcase import ItemMixinTestCase


class TestItemMixinTankingEhp(ItemMixinTestCase):

    def setUp(self):
        ItemMixinTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.hp)
        self.mkattr(attr_id=AttrId.em_dmg_resonance)
        self.mkattr(attr_id=AttrId.therm_dmg_resonance)
        self.mkattr(attr_id=AttrId.kin_dmg_resonance)
        self.mkattr(attr_id=AttrId.expl_dmg_resonance)
        self.mkattr(attr_id=AttrId.armor_hp)
        self.mkattr(attr_id=AttrId.armor_em_dmg_resonance)
        self.mkattr(attr_id=AttrId.armor_therm_dmg_resonance)
        self.mkattr(attr_id=AttrId.armor_kin_dmg_resonance)
        self.mkattr(attr_id=AttrId.armor_expl_dmg_resonance)
        self.mkattr(attr_id=AttrId.shield_capacity)
        self.mkattr(attr_id=AttrId.shield_em_dmg_resonance)
        self.mkattr(attr_id=AttrId.shield_therm_dmg_resonance)
        self.mkattr(attr_id=AttrId.shield_kin_dmg_resonance)
        self.mkattr(attr_id=AttrId.shield_expl_dmg_resonance)

    def test_uniform(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
            AttrId.hp: 1,
            AttrId.em_dmg_resonance: 0.8,
            AttrId.therm_dmg_resonance: 0.8,
            AttrId.kin_dmg_resonance: 0.8,
            AttrId.expl_dmg_resonance: 0.8,
            AttrId.armor_hp: 10,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_therm_dmg_resonance: 0.4,
            AttrId.armor_kin_dmg_resonance: 0.4,
            AttrId.armor_expl_dmg_resonance: 0.4,
            AttrId.shield_capacity: 100,
            AttrId.shield_em_dmg_resonance: 0.2,
            AttrId.shield_therm_dmg_resonance: 0.2,
            AttrId.shield_kin_dmg_resonance: 0.2,
            AttrId.shield_expl_dmg_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        results = item.get_ehp(DmgProfile(1, 1, 1, 1))
        self.assertAlmostEqual(results.hull, 1.25)
        self.assertAlmostEqual(results.armor, 25)
        self.assertAlmostEqual(results.shield, 500)
        self.assertAlmostEqual(results.total, 526.25)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_non_uniform(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
            AttrId.hp: 10,
            AttrId.em_dmg_resonance: 0.9,
            AttrId.therm_dmg_resonance: 0.8,
            AttrId.kin_dmg_resonance: 0.7,
            AttrId.expl_dmg_resonance: 0.6,
            AttrId.armor_hp: 50,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_therm_dmg_resonance: 0.6,
            AttrId.armor_kin_dmg_resonance: 0.8,
            AttrId.armor_expl_dmg_resonance: 0.9,
            AttrId.shield_capacity: 600,
            AttrId.shield_em_dmg_resonance: 1.0,
            AttrId.shield_therm_dmg_resonance: 0.8,
            AttrId.shield_kin_dmg_resonance: 0.6,
            AttrId.shield_expl_dmg_resonance: 0.5}).id)
        fit.ship = item
        # Verification
        results = item.get_ehp(DmgProfile(25, 6, 8.333, 1))
        self.assertAlmostEqual(results.hull, 11.957, places=3)
        self.assertAlmostEqual(results.armor, 95.276, places=3)
        self.assertAlmostEqual(results.shield, 685.551, places=3)
        self.assertAlmostEqual(results.total, 792.783, places=3)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_hp_hull(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
            AttrId.em_dmg_resonance: 0.9,
            AttrId.therm_dmg_resonance: 0.8,
            AttrId.kin_dmg_resonance: 0.7,
            AttrId.expl_dmg_resonance: 0.6,
            AttrId.armor_hp: 50,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_therm_dmg_resonance: 0.6,
            AttrId.armor_kin_dmg_resonance: 0.8,
            AttrId.armor_expl_dmg_resonance: 0.9,
            AttrId.shield_capacity: 600,
            AttrId.shield_em_dmg_resonance: 1.0,
            AttrId.shield_therm_dmg_resonance: 0.8,
            AttrId.shield_kin_dmg_resonance: 0.6,
            AttrId.shield_expl_dmg_resonance: 0.5}).id)
        fit.ship = item
        # Verification
        results = item.get_ehp(DmgProfile(25, 6, 8.333, 1))
        self.assertAlmostEqual(results.hull, 0)
        self.assertAlmostEqual(results.armor, 95.276, places=3)
        self.assertAlmostEqual(results.shield, 685.551, places=3)
        self.assertAlmostEqual(results.total, 780.827, places=3)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_hp_armor(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
            AttrId.hp: 10,
            AttrId.em_dmg_resonance: 0.9,
            AttrId.therm_dmg_resonance: 0.8,
            AttrId.kin_dmg_resonance: 0.7,
            AttrId.expl_dmg_resonance: 0.6,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_therm_dmg_resonance: 0.6,
            AttrId.armor_kin_dmg_resonance: 0.8,
            AttrId.armor_expl_dmg_resonance: 0.9,
            AttrId.shield_capacity: 600,
            AttrId.shield_em_dmg_resonance: 1.0,
            AttrId.shield_therm_dmg_resonance: 0.8,
            AttrId.shield_kin_dmg_resonance: 0.6,
            AttrId.shield_expl_dmg_resonance: 0.5}).id)
        fit.ship = item
        # Verification
        results = item.get_ehp(DmgProfile(25, 6, 8.333, 1))
        self.assertAlmostEqual(results.hull, 11.957, places=3)
        self.assertAlmostEqual(results.armor, 0)
        self.assertAlmostEqual(results.shield, 685.551, places=3)
        self.assertAlmostEqual(results.total, 697.507, places=3)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_hp_shield(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
            AttrId.hp: 10,
            AttrId.em_dmg_resonance: 0.9,
            AttrId.therm_dmg_resonance: 0.8,
            AttrId.kin_dmg_resonance: 0.7,
            AttrId.expl_dmg_resonance: 0.6,
            AttrId.armor_hp: 50,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_therm_dmg_resonance: 0.6,
            AttrId.armor_kin_dmg_resonance: 0.8,
            AttrId.armor_expl_dmg_resonance: 0.9,
            AttrId.shield_em_dmg_resonance: 1.0,
            AttrId.shield_therm_dmg_resonance: 0.8,
            AttrId.shield_kin_dmg_resonance: 0.6,
            AttrId.shield_expl_dmg_resonance: 0.5}).id)
        fit.ship = item
        # Verification
        results = item.get_ehp(DmgProfile(25, 6, 8.333, 1))
        self.assertAlmostEqual(results.hull, 11.957, places=3)
        self.assertAlmostEqual(results.armor, 95.276, places=3)
        self.assertAlmostEqual(results.shield, 0)
        self.assertAlmostEqual(results.total, 107.233, places=3)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_hp_all(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
            AttrId.em_dmg_resonance: 0.9,
            AttrId.therm_dmg_resonance: 0.8,
            AttrId.kin_dmg_resonance: 0.7,
            AttrId.expl_dmg_resonance: 0.6,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_therm_dmg_resonance: 0.6,
            AttrId.armor_kin_dmg_resonance: 0.8,
            AttrId.armor_expl_dmg_resonance: 0.9,
            AttrId.shield_em_dmg_resonance: 1.0,
            AttrId.shield_therm_dmg_resonance: 0.8,
            AttrId.shield_kin_dmg_resonance: 0.6,
            AttrId.shield_expl_dmg_resonance: 0.5}).id)
        fit.ship = item
        # Verification
        results = item.get_ehp(DmgProfile(25, 6, 8.333, 1))
        self.assertAlmostEqual(results.hull, 0)
        self.assertAlmostEqual(results.armor, 0)
        self.assertAlmostEqual(results.shield, 0)
        self.assertAlmostEqual(results.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_resist_em(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
            AttrId.hp: 10,
            AttrId.em_dmg_resonance: 0.9,
            AttrId.therm_dmg_resonance: 0.8,
            AttrId.kin_dmg_resonance: 0.7,
            AttrId.expl_dmg_resonance: 0.6,
            AttrId.armor_hp: 50,
            AttrId.armor_therm_dmg_resonance: 0.6,
            AttrId.armor_kin_dmg_resonance: 0.8,
            AttrId.armor_expl_dmg_resonance: 0.9,
            AttrId.shield_capacity: 600,
            AttrId.shield_em_dmg_resonance: 1.0,
            AttrId.shield_therm_dmg_resonance: 0.8,
            AttrId.shield_kin_dmg_resonance: 0.6,
            AttrId.shield_expl_dmg_resonance: 0.5}).id)
        fit.ship = item
        # Verification
        results = item.get_ehp(DmgProfile(25, 6, 8.333, 1))
        self.assertAlmostEqual(results.hull, 11.957, places=3)
        self.assertAlmostEqual(results.armor, 55.760, places=3)
        self.assertAlmostEqual(results.shield, 685.551, places=3)
        self.assertAlmostEqual(results.total, 753.267, places=3)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_resist_therm(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
            AttrId.hp: 10,
            AttrId.em_dmg_resonance: 0.9,
            AttrId.therm_dmg_resonance: 0.8,
            AttrId.kin_dmg_resonance: 0.7,
            AttrId.expl_dmg_resonance: 0.6,
            AttrId.armor_hp: 50,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_therm_dmg_resonance: 0.6,
            AttrId.armor_kin_dmg_resonance: 0.8,
            AttrId.armor_expl_dmg_resonance: 0.9,
            AttrId.shield_capacity: 600,
            AttrId.shield_em_dmg_resonance: 1.0,
            AttrId.shield_kin_dmg_resonance: 0.6,
            AttrId.shield_expl_dmg_resonance: 0.5}).id)
        fit.ship = item
        # Verification
        results = item.get_ehp(DmgProfile(25, 6, 8.333, 1))
        self.assertAlmostEqual(results.hull, 11.957, places=3)
        self.assertAlmostEqual(results.armor, 95.276, places=3)
        self.assertAlmostEqual(results.shield, 663.012, places=3)
        self.assertAlmostEqual(results.total, 770.244, places=3)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_resist_kin(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
            AttrId.hp: 10,
            AttrId.em_dmg_resonance: 0.9,
            AttrId.therm_dmg_resonance: 0.8,
            AttrId.expl_dmg_resonance: 0.6,
            AttrId.armor_hp: 50,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_therm_dmg_resonance: 0.6,
            AttrId.armor_kin_dmg_resonance: 0.8,
            AttrId.armor_expl_dmg_resonance: 0.9,
            AttrId.shield_capacity: 600,
            AttrId.shield_em_dmg_resonance: 1.0,
            AttrId.shield_therm_dmg_resonance: 0.8,
            AttrId.shield_kin_dmg_resonance: 0.6,
            AttrId.shield_expl_dmg_resonance: 0.5}).id)
        fit.ship = item
        # Verification
        results = item.get_ehp(DmgProfile(25, 6, 8.333, 1))
        self.assertAlmostEqual(results.hull, 11.132, places=3)
        self.assertAlmostEqual(results.armor, 95.276, places=3)
        self.assertAlmostEqual(results.shield, 685.551, places=3)
        self.assertAlmostEqual(results.total, 791.958, places=3)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_resist_expl(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
            AttrId.hp: 10,
            AttrId.em_dmg_resonance: 0.9,
            AttrId.therm_dmg_resonance: 0.8,
            AttrId.kin_dmg_resonance: 0.7,
            AttrId.expl_dmg_resonance: 0.6,
            AttrId.armor_hp: 50,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_therm_dmg_resonance: 0.6,
            AttrId.armor_kin_dmg_resonance: 0.8,
            AttrId.shield_capacity: 600,
            AttrId.shield_em_dmg_resonance: 1.0,
            AttrId.shield_therm_dmg_resonance: 0.8,
            AttrId.shield_kin_dmg_resonance: 0.6,
            AttrId.shield_expl_dmg_resonance: 0.5}).id)
        fit.ship = item
        # Verification
        results = item.get_ehp(DmgProfile(25, 6, 8.333, 1))
        self.assertAlmostEqual(results.hull, 11.957, places=3)
        self.assertAlmostEqual(results.armor, 94.828, places=3)
        self.assertAlmostEqual(results.shield, 685.551, places=3)
        self.assertAlmostEqual(results.total, 792.335, places=3)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_resist_all(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
            AttrId.hp: 10,
            AttrId.em_dmg_resonance: 0.9,
            AttrId.therm_dmg_resonance: 0.8,
            AttrId.kin_dmg_resonance: 0.7,
            AttrId.expl_dmg_resonance: 0.6,
            AttrId.armor_hp: 50,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_therm_dmg_resonance: 0.6,
            AttrId.armor_kin_dmg_resonance: 0.8,
            AttrId.armor_expl_dmg_resonance: 0.9,
            AttrId.shield_capacity: 600}).id)
        fit.ship = item
        # Verification
        results = item.get_ehp(DmgProfile(25, 6, 8.333, 1))
        self.assertAlmostEqual(results.hull, 11.957, places=3)
        self.assertAlmostEqual(results.armor, 95.276, places=3)
        self.assertAlmostEqual(results.shield, 600, places=3)
        self.assertAlmostEqual(results.total, 707.233, places=3)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_source_none(self):
        fit = Fit(source=None)
        item = Ship(self.mktype(attrs={
            AttrId.hp: 1,
            AttrId.em_dmg_resonance: 0.8,
            AttrId.therm_dmg_resonance: 0.8,
            AttrId.kin_dmg_resonance: 0.8,
            AttrId.expl_dmg_resonance: 0.8,
            AttrId.armor_hp: 10,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_therm_dmg_resonance: 0.4,
            AttrId.armor_kin_dmg_resonance: 0.4,
            AttrId.armor_expl_dmg_resonance: 0.4,
            AttrId.shield_capacity: 100,
            AttrId.shield_em_dmg_resonance: 0.2,
            AttrId.shield_therm_dmg_resonance: 0.2,
            AttrId.shield_kin_dmg_resonance: 0.2,
            AttrId.shield_expl_dmg_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        results = item.get_ehp(DmgProfile(1, 1, 1, 1))
        self.assertAlmostEqual(results.hull, 0)
        self.assertAlmostEqual(results.armor, 0)
        self.assertAlmostEqual(results.shield, 0)
        self.assertAlmostEqual(results.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)
