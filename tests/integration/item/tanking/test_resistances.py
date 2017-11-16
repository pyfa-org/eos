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


class TestItemMixinTankingResists(ItemMixinTestCase):

    def setUp(self):
        ItemMixinTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.em_dmg_resonance)
        self.mkattr(attr_id=AttrId.thermal_dmg_resonance)
        self.mkattr(attr_id=AttrId.kinetic_dmg_resonance)
        self.mkattr(attr_id=AttrId.explosive_dmg_resonance)
        self.mkattr(attr_id=AttrId.armor_em_dmg_resonance)
        self.mkattr(attr_id=AttrId.armor_thermal_dmg_resonance)
        self.mkattr(attr_id=AttrId.armor_kinetic_dmg_resonance)
        self.mkattr(attr_id=AttrId.armor_explosive_dmg_resonance)
        self.mkattr(attr_id=AttrId.shield_em_dmg_resonance)
        self.mkattr(attr_id=AttrId.shield_thermal_dmg_resonance)
        self.mkattr(attr_id=AttrId.shield_kinetic_dmg_resonance)
        self.mkattr(attr_id=AttrId.shield_explosive_dmg_resonance)

    def test_generic(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
            AttrId.em_dmg_resonance: 0.01,
            AttrId.thermal_dmg_resonance: 0.02,
            AttrId.kinetic_dmg_resonance: 0.03,
            AttrId.explosive_dmg_resonance: 0.04,
            AttrId.armor_em_dmg_resonance: 0.05,
            AttrId.armor_thermal_dmg_resonance: 0.06,
            AttrId.armor_kinetic_dmg_resonance: 0.07,
            AttrId.armor_explosive_dmg_resonance: 0.08,
            AttrId.shield_em_dmg_resonance: 0.09,
            AttrId.shield_thermal_dmg_resonance: 0.1,
            AttrId.shield_kinetic_dmg_resonance: 0.11,
            AttrId.shield_explosive_dmg_resonance: 0.12}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.resists.hull.em, 0.99)
        self.assertAlmostEqual(item.resists.hull.thermal, 0.98)
        self.assertAlmostEqual(item.resists.hull.kinetic, 0.97)
        self.assertAlmostEqual(item.resists.hull.explosive, 0.96)
        self.assertAlmostEqual(item.resists.armor.em, 0.95)
        self.assertAlmostEqual(item.resists.armor.thermal, 0.94)
        self.assertAlmostEqual(item.resists.armor.kinetic, 0.93)
        self.assertAlmostEqual(item.resists.armor.explosive, 0.92)
        self.assertAlmostEqual(item.resists.shield.em, 0.91)
        self.assertAlmostEqual(item.resists.shield.thermal, 0.9)
        self.assertAlmostEqual(item.resists.shield.kinetic, 0.89)
        self.assertAlmostEqual(item.resists.shield.explosive, 0.88)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_attr(self):
        fit = Fit()
        item = Ship(self.mktype().id)
        fit.ship = item
        # Verification
        self.assertIsNone(item.resists.hull.em)
        self.assertIsNone(item.resists.hull.thermal)
        self.assertIsNone(item.resists.hull.kinetic)
        self.assertIsNone(item.resists.hull.explosive)
        self.assertIsNone(item.resists.armor.em)
        self.assertIsNone(item.resists.armor.thermal)
        self.assertIsNone(item.resists.armor.kinetic)
        self.assertIsNone(item.resists.armor.explosive)
        self.assertIsNone(item.resists.shield.em)
        self.assertIsNone(item.resists.shield.thermal)
        self.assertIsNone(item.resists.shield.kinetic)
        self.assertIsNone(item.resists.shield.explosive)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_source(self):
        fit = Fit(source=None)
        item = Ship(self.mktype(attrs={
            AttrId.em_dmg_resonance: 0.01,
            AttrId.thermal_dmg_resonance: 0.02,
            AttrId.kinetic_dmg_resonance: 0.03,
            AttrId.explosive_dmg_resonance: 0.04,
            AttrId.armor_em_dmg_resonance: 0.05,
            AttrId.armor_thermal_dmg_resonance: 0.06,
            AttrId.armor_kinetic_dmg_resonance: 0.07,
            AttrId.armor_explosive_dmg_resonance: 0.08,
            AttrId.shield_em_dmg_resonance: 0.09,
            AttrId.shield_thermal_dmg_resonance: 0.1,
            AttrId.shield_kinetic_dmg_resonance: 0.11,
            AttrId.shield_explosive_dmg_resonance: 0.12}).id)
        fit.ship = item
        # Verification
        self.assertIsNone(item.resists.hull.em)
        self.assertIsNone(item.resists.hull.thermal)
        self.assertIsNone(item.resists.hull.kinetic)
        self.assertIsNone(item.resists.hull.explosive)
        self.assertIsNone(item.resists.armor.em)
        self.assertIsNone(item.resists.armor.thermal)
        self.assertIsNone(item.resists.armor.kinetic)
        self.assertIsNone(item.resists.armor.explosive)
        self.assertIsNone(item.resists.shield.em)
        self.assertIsNone(item.resists.shield.thermal)
        self.assertIsNone(item.resists.shield.kinetic)
        self.assertIsNone(item.resists.shield.explosive)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)
