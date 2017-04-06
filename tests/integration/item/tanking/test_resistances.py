# ===============================================================================
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
# ===============================================================================


from eos import *
from eos.const.eve import Attribute
from tests.integration.item.item_testcase import ItemMixinTestCase


class TestItemMixinTankingResistances(ItemMixinTestCase):

    def setUp(self):
        super().setUp()
        self.ch.attribute(attribute_id=Attribute.em_damage_resonance)
        self.ch.attribute(attribute_id=Attribute.thermal_damage_resonance)
        self.ch.attribute(attribute_id=Attribute.kinetic_damage_resonance)
        self.ch.attribute(attribute_id=Attribute.explosive_damage_resonance)
        self.ch.attribute(attribute_id=Attribute.armor_em_damage_resonance)
        self.ch.attribute(attribute_id=Attribute.armor_thermal_damage_resonance)
        self.ch.attribute(attribute_id=Attribute.armor_kinetic_damage_resonance)
        self.ch.attribute(attribute_id=Attribute.armor_explosive_damage_resonance)
        self.ch.attribute(attribute_id=Attribute.shield_em_damage_resonance)
        self.ch.attribute(attribute_id=Attribute.shield_thermal_damage_resonance)
        self.ch.attribute(attribute_id=Attribute.shield_kinetic_damage_resonance)
        self.ch.attribute(attribute_id=Attribute.shield_explosive_damage_resonance)

    def test_generic(self):
        fit = Fit()
        item = Ship(self.ch.type(attributes={
            Attribute.em_damage_resonance: 0.01, Attribute.thermal_damage_resonance: 0.02,
            Attribute.kinetic_damage_resonance: 0.03, Attribute.explosive_damage_resonance: 0.04,
            Attribute.armor_em_damage_resonance: 0.05, Attribute.armor_thermal_damage_resonance: 0.06,
            Attribute.armor_kinetic_damage_resonance: 0.07, Attribute.armor_explosive_damage_resonance: 0.08,
            Attribute.shield_em_damage_resonance: 0.09, Attribute.shield_thermal_damage_resonance: 0.1,
            Attribute.shield_kinetic_damage_resonance: 0.11, Attribute.shield_explosive_damage_resonance: 0.12
        }).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.resistances.hull.em, 0.99)
        self.assertAlmostEqual(item.resistances.hull.thermal, 0.98)
        self.assertAlmostEqual(item.resistances.hull.kinetic, 0.97)
        self.assertAlmostEqual(item.resistances.hull.explosive, 0.96)
        self.assertAlmostEqual(item.resistances.armor.em, 0.95)
        self.assertAlmostEqual(item.resistances.armor.thermal, 0.94)
        self.assertAlmostEqual(item.resistances.armor.kinetic, 0.93)
        self.assertAlmostEqual(item.resistances.armor.explosive, 0.92)
        self.assertAlmostEqual(item.resistances.shield.em, 0.91)
        self.assertAlmostEqual(item.resistances.shield.thermal, 0.9)
        self.assertAlmostEqual(item.resistances.shield.kinetic, 0.89)
        self.assertAlmostEqual(item.resistances.shield.explosive, 0.88)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_no_attr(self):
        fit = Fit()
        item = Ship(self.ch.type().id)
        fit.ship = item
        # Verification
        self.assertIsNone(item.resistances.hull.em)
        self.assertIsNone(item.resistances.hull.thermal)
        self.assertIsNone(item.resistances.hull.kinetic)
        self.assertIsNone(item.resistances.hull.explosive)
        self.assertIsNone(item.resistances.armor.em)
        self.assertIsNone(item.resistances.armor.thermal)
        self.assertIsNone(item.resistances.armor.kinetic)
        self.assertIsNone(item.resistances.armor.explosive)
        self.assertIsNone(item.resistances.shield.em)
        self.assertIsNone(item.resistances.shield.thermal)
        self.assertIsNone(item.resistances.shield.kinetic)
        self.assertIsNone(item.resistances.shield.explosive)
        # Cleanup
        self.assertEqual(len(self.log), 12)
        self.assert_fit_buffers_empty(fit)

    def test_no_source(self):
        fit = Fit(source=None)
        item = Ship(self.ch.type(attributes={
            Attribute.em_damage_resonance: 0.01, Attribute.thermal_damage_resonance: 0.02,
            Attribute.kinetic_damage_resonance: 0.03, Attribute.explosive_damage_resonance: 0.04,
            Attribute.armor_em_damage_resonance: 0.05, Attribute.armor_thermal_damage_resonance: 0.06,
            Attribute.armor_kinetic_damage_resonance: 0.07, Attribute.armor_explosive_damage_resonance: 0.08,
            Attribute.shield_em_damage_resonance: 0.09, Attribute.shield_thermal_damage_resonance: 0.1,
            Attribute.shield_kinetic_damage_resonance: 0.11, Attribute.shield_explosive_damage_resonance: 0.12
        }).id)
        fit.ship = item
        # Verification
        self.assertIsNone(item.resistances.hull.em)
        self.assertIsNone(item.resistances.hull.thermal)
        self.assertIsNone(item.resistances.hull.kinetic)
        self.assertIsNone(item.resistances.hull.explosive)
        self.assertIsNone(item.resistances.armor.em)
        self.assertIsNone(item.resistances.armor.thermal)
        self.assertIsNone(item.resistances.armor.kinetic)
        self.assertIsNone(item.resistances.armor.explosive)
        self.assertIsNone(item.resistances.shield.em)
        self.assertIsNone(item.resistances.shield.thermal)
        self.assertIsNone(item.resistances.shield.kinetic)
        self.assertIsNone(item.resistances.shield.explosive)
        # Cleanup
        self.assertEqual(len(self.log), 12)
        self.assert_fit_buffers_empty(fit)
