# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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

    def test_equal(self):
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
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 526.25)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_worst_em(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
            AttrId.hp: 1,
            AttrId.em_dmg_resonance: 0.8,
            AttrId.therm_dmg_resonance: 0.7,
            AttrId.kin_dmg_resonance: 0.7,
            AttrId.expl_dmg_resonance: 0.7,
            AttrId.armor_hp: 10,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_therm_dmg_resonance: 0.3,
            AttrId.armor_kin_dmg_resonance: 0.3,
            AttrId.armor_expl_dmg_resonance: 0.3,
            AttrId.shield_capacity: 100,
            AttrId.shield_em_dmg_resonance: 0.2,
            AttrId.shield_therm_dmg_resonance: 0.1,
            AttrId.shield_kin_dmg_resonance: 0.1,
            AttrId.shield_expl_dmg_resonance: 0.1}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 526.25)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_worst_therm(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
            AttrId.hp: 1,
            AttrId.em_dmg_resonance: 0.7,
            AttrId.therm_dmg_resonance: 0.8,
            AttrId.kin_dmg_resonance: 0.7,
            AttrId.expl_dmg_resonance: 0.7,
            AttrId.armor_hp: 10,
            AttrId.armor_em_dmg_resonance: 0.3,
            AttrId.armor_therm_dmg_resonance: 0.4,
            AttrId.armor_kin_dmg_resonance: 0.3,
            AttrId.armor_expl_dmg_resonance: 0.3,
            AttrId.shield_capacity: 100,
            AttrId.shield_em_dmg_resonance: 0.1,
            AttrId.shield_therm_dmg_resonance: 0.2,
            AttrId.shield_kin_dmg_resonance: 0.1,
            AttrId.shield_expl_dmg_resonance: 0.1}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 526.25)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_worst_kin(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
            AttrId.hp: 1,
            AttrId.em_dmg_resonance: 0.7,
            AttrId.therm_dmg_resonance: 0.7,
            AttrId.kin_dmg_resonance: 0.8,
            AttrId.expl_dmg_resonance: 0.7,
            AttrId.armor_hp: 10,
            AttrId.armor_em_dmg_resonance: 0.3,
            AttrId.armor_therm_dmg_resonance: 0.3,
            AttrId.armor_kin_dmg_resonance: 0.4,
            AttrId.armor_expl_dmg_resonance: 0.3,
            AttrId.shield_capacity: 100,
            AttrId.shield_em_dmg_resonance: 0.1,
            AttrId.shield_therm_dmg_resonance: 0.1,
            AttrId.shield_kin_dmg_resonance: 0.2,
            AttrId.shield_expl_dmg_resonance: 0.1}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 526.25)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_worst_expl(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
            AttrId.hp: 1,
            AttrId.em_dmg_resonance: 0.7,
            AttrId.therm_dmg_resonance: 0.7,
            AttrId.kin_dmg_resonance: 0.7,
            AttrId.expl_dmg_resonance: 0.8,
            AttrId.armor_hp: 10,
            AttrId.armor_em_dmg_resonance: 0.3,
            AttrId.armor_therm_dmg_resonance: 0.3,
            AttrId.armor_kin_dmg_resonance: 0.3,
            AttrId.armor_expl_dmg_resonance: 0.4,
            AttrId.shield_capacity: 100,
            AttrId.shield_em_dmg_resonance: 0.1,
            AttrId.shield_therm_dmg_resonance: 0.1,
            AttrId.shield_kin_dmg_resonance: 0.1,
            AttrId.shield_expl_dmg_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 526.25)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_mixed(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
            AttrId.hp: 1,
            AttrId.em_dmg_resonance: 0.8,
            AttrId.therm_dmg_resonance: 0.7,
            AttrId.kin_dmg_resonance: 0.7,
            AttrId.expl_dmg_resonance: 0.8,
            AttrId.armor_hp: 10,
            AttrId.armor_em_dmg_resonance: 0.3,
            AttrId.armor_therm_dmg_resonance: 0.4,
            AttrId.armor_kin_dmg_resonance: 0.4,
            AttrId.armor_expl_dmg_resonance: 0.3,
            AttrId.shield_capacity: 100,
            AttrId.shield_em_dmg_resonance: 0.1,
            AttrId.shield_therm_dmg_resonance: 0.1,
            AttrId.shield_kin_dmg_resonance: 0.2,
            AttrId.shield_expl_dmg_resonance: 0.01}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 526.25)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_item_attr_hp_hull_absent(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
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
        self.assertAlmostEqual(item.worst_case_ehp.hull, 0)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 525)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_item_attr_hp_armor_absent(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
            AttrId.hp: 1,
            AttrId.em_dmg_resonance: 0.8,
            AttrId.therm_dmg_resonance: 0.8,
            AttrId.kin_dmg_resonance: 0.8,
            AttrId.expl_dmg_resonance: 0.8,
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
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 0)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 501.25)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_item_attr_hp_shield_absent(self):
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
            AttrId.shield_em_dmg_resonance: 0.2,
            AttrId.shield_therm_dmg_resonance: 0.2,
            AttrId.shield_kin_dmg_resonance: 0.2,
            AttrId.shield_expl_dmg_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 0)
        self.assertAlmostEqual(item.worst_case_ehp.total, 26.25)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_item_attr_hp_all_absent(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
            AttrId.em_dmg_resonance: 0.8,
            AttrId.therm_dmg_resonance: 0.8,
            AttrId.kin_dmg_resonance: 0.8,
            AttrId.expl_dmg_resonance: 0.8,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_therm_dmg_resonance: 0.4,
            AttrId.armor_kin_dmg_resonance: 0.4,
            AttrId.armor_expl_dmg_resonance: 0.4,
            AttrId.shield_em_dmg_resonance: 0.2,
            AttrId.shield_therm_dmg_resonance: 0.2,
            AttrId.shield_kin_dmg_resonance: 0.2,
            AttrId.shield_expl_dmg_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 0)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 0)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 0)
        self.assertAlmostEqual(item.worst_case_ehp.total, 0)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_item_attr_resist_em_absent(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
            AttrId.hp: 1,
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
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 526)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_item_attr_resist_therm_absent(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
            AttrId.hp: 1,
            AttrId.em_dmg_resonance: 0.8,
            AttrId.therm_dmg_resonance: 0.8,
            AttrId.kin_dmg_resonance: 0.8,
            AttrId.expl_dmg_resonance: 0.8,
            AttrId.armor_hp: 10,
            AttrId.armor_em_dmg_resonance: 0.4,
            AttrId.armor_kin_dmg_resonance: 0.4,
            AttrId.armor_expl_dmg_resonance: 0.4,
            AttrId.shield_capacity: 100,
            AttrId.shield_em_dmg_resonance: 0.2,
            AttrId.shield_therm_dmg_resonance: 0.2,
            AttrId.shield_kin_dmg_resonance: 0.2,
            AttrId.shield_expl_dmg_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 10)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 511.25)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_item_attr_resist_kin_absent(self):
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
            AttrId.shield_expl_dmg_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 100)
        self.assertAlmostEqual(item.worst_case_ehp.total, 126.25)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_item_attr_resist_expl_absent(self):
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
            AttrId.shield_capacity: 100,
            AttrId.shield_em_dmg_resonance: 0.2,
            AttrId.shield_therm_dmg_resonance: 0.2,
            AttrId.shield_kin_dmg_resonance: 0.2,
            AttrId.shield_expl_dmg_resonance: 0.2}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 10)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(item.worst_case_ehp.total, 511.25)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_item_attr_resist_all_absent(self):
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
            AttrId.shield_capacity: 100}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 100)
        self.assertAlmostEqual(item.worst_case_ehp.total, 126.25)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_item_not_loaded(self):
        fit = Fit()
        item = Ship(self.allocate_type_id())
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.worst_case_ehp.hull, 0)
        self.assertAlmostEqual(item.worst_case_ehp.armor, 0)
        self.assertAlmostEqual(item.worst_case_ehp.shield, 0)
        self.assertAlmostEqual(item.worst_case_ehp.total, 0)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)
