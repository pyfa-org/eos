# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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


from eos.const.eve import Attribute
from eos.fit.holder.mixin.tanking import BufferTankingMixin
from tests.fit.fit_testcase import FitTestCase


class TestHolderMixinTankingResistances(FitTestCase):

    def setUp(self):
        super().setUp()
        self.mixin = BufferTankingMixin()
        self.mixin.attributes = {}

    def test_generic(self):
        self.mixin.attributes[Attribute.em_damage_resonance] = 0.01
        self.mixin.attributes[Attribute.thermal_damage_resonance] = 0.02
        self.mixin.attributes[Attribute.kinetic_damage_resonance] = 0.03
        self.mixin.attributes[Attribute.explosive_damage_resonance] = 0.04
        self.mixin.attributes[Attribute.armor_em_damage_resonance] = 0.05
        self.mixin.attributes[Attribute.armor_thermal_damage_resonance] = 0.06
        self.mixin.attributes[Attribute.armor_kinetic_damage_resonance] = 0.07
        self.mixin.attributes[Attribute.armor_explosive_damage_resonance] = 0.08
        self.mixin.attributes[Attribute.shield_em_damage_resonance] = 0.09
        self.mixin.attributes[Attribute.shield_thermal_damage_resonance] = 0.1
        self.mixin.attributes[Attribute.shield_kinetic_damage_resonance] = 0.11
        self.mixin.attributes[Attribute.shield_explosive_damage_resonance] = 0.12
        self.assertAlmostEqual(self.mixin.resistances.hull.em, 0.99)
        self.assertAlmostEqual(self.mixin.resistances.hull.thermal, 0.98)
        self.assertAlmostEqual(self.mixin.resistances.hull.kinetic, 0.97)
        self.assertAlmostEqual(self.mixin.resistances.hull.explosive, 0.96)
        self.assertAlmostEqual(self.mixin.resistances.armor.em, 0.95)
        self.assertAlmostEqual(self.mixin.resistances.armor.thermal, 0.94)
        self.assertAlmostEqual(self.mixin.resistances.armor.kinetic, 0.93)
        self.assertAlmostEqual(self.mixin.resistances.armor.explosive, 0.92)
        self.assertAlmostEqual(self.mixin.resistances.shield.em, 0.91)
        self.assertAlmostEqual(self.mixin.resistances.shield.thermal, 0.9)
        self.assertAlmostEqual(self.mixin.resistances.shield.kinetic, 0.89)
        self.assertAlmostEqual(self.mixin.resistances.shield.explosive, 0.88)

    def test_no_attr(self):
        self.assertIsNone(self.mixin.resistances.hull.em)
        self.assertIsNone(self.mixin.resistances.hull.thermal)
        self.assertIsNone(self.mixin.resistances.hull.kinetic)
        self.assertIsNone(self.mixin.resistances.hull.explosive)
        self.assertIsNone(self.mixin.resistances.armor.em)
        self.assertIsNone(self.mixin.resistances.armor.thermal)
        self.assertIsNone(self.mixin.resistances.armor.kinetic)
        self.assertIsNone(self.mixin.resistances.armor.explosive)
        self.assertIsNone(self.mixin.resistances.shield.em)
        self.assertIsNone(self.mixin.resistances.shield.thermal)
        self.assertIsNone(self.mixin.resistances.shield.kinetic)
        self.assertIsNone(self.mixin.resistances.shield.explosive)

    def test_cache(self):
        self.mixin.attributes[Attribute.em_damage_resonance] = 0.01
        self.mixin.attributes[Attribute.thermal_damage_resonance] = 0.02
        self.mixin.attributes[Attribute.kinetic_damage_resonance] = 0.03
        self.mixin.attributes[Attribute.explosive_damage_resonance] = 0.04
        self.mixin.attributes[Attribute.armor_em_damage_resonance] = 0.05
        self.mixin.attributes[Attribute.armor_thermal_damage_resonance] = 0.06
        self.mixin.attributes[Attribute.armor_kinetic_damage_resonance] = 0.07
        self.mixin.attributes[Attribute.armor_explosive_damage_resonance] = 0.08
        self.mixin.attributes[Attribute.shield_em_damage_resonance] = 0.09
        self.mixin.attributes[Attribute.shield_thermal_damage_resonance] = 0.1
        self.mixin.attributes[Attribute.shield_kinetic_damage_resonance] = 0.11
        self.mixin.attributes[Attribute.shield_explosive_damage_resonance] = 0.12
        self.assertAlmostEqual(self.mixin.resistances.hull.em, 0.99)
        self.assertAlmostEqual(self.mixin.resistances.hull.thermal, 0.98)
        self.assertAlmostEqual(self.mixin.resistances.hull.kinetic, 0.97)
        self.assertAlmostEqual(self.mixin.resistances.hull.explosive, 0.96)
        self.assertAlmostEqual(self.mixin.resistances.armor.em, 0.95)
        self.assertAlmostEqual(self.mixin.resistances.armor.thermal, 0.94)
        self.assertAlmostEqual(self.mixin.resistances.armor.kinetic, 0.93)
        self.assertAlmostEqual(self.mixin.resistances.armor.explosive, 0.92)
        self.assertAlmostEqual(self.mixin.resistances.shield.em, 0.91)
        self.assertAlmostEqual(self.mixin.resistances.shield.thermal, 0.9)
        self.assertAlmostEqual(self.mixin.resistances.shield.kinetic, 0.89)
        self.assertAlmostEqual(self.mixin.resistances.shield.explosive, 0.88)
        self.mixin.attributes[Attribute.em_damage_resonance] = 0.11
        self.mixin.attributes[Attribute.thermal_damage_resonance] = 0.12
        self.mixin.attributes[Attribute.kinetic_damage_resonance] = 0.13
        self.mixin.attributes[Attribute.explosive_damage_resonance] = 0.14
        self.mixin.attributes[Attribute.armor_em_damage_resonance] = 0.15
        self.mixin.attributes[Attribute.armor_thermal_damage_resonance] = 0.16
        self.mixin.attributes[Attribute.armor_kinetic_damage_resonance] = 0.17
        self.mixin.attributes[Attribute.armor_explosive_damage_resonance] = 0.108
        self.mixin.attributes[Attribute.shield_em_damage_resonance] = 0.19
        self.mixin.attributes[Attribute.shield_thermal_damage_resonance] = 0.2
        self.mixin.attributes[Attribute.shield_kinetic_damage_resonance] = 0.21
        self.mixin.attributes[Attribute.shield_explosive_damage_resonance] = 0.22
        self.assertAlmostEqual(self.mixin.resistances.hull.em, 0.99)
        self.assertAlmostEqual(self.mixin.resistances.hull.thermal, 0.98)
        self.assertAlmostEqual(self.mixin.resistances.hull.kinetic, 0.97)
        self.assertAlmostEqual(self.mixin.resistances.hull.explosive, 0.96)
        self.assertAlmostEqual(self.mixin.resistances.armor.em, 0.95)
        self.assertAlmostEqual(self.mixin.resistances.armor.thermal, 0.94)
        self.assertAlmostEqual(self.mixin.resistances.armor.kinetic, 0.93)
        self.assertAlmostEqual(self.mixin.resistances.armor.explosive, 0.92)
        self.assertAlmostEqual(self.mixin.resistances.shield.em, 0.91)
        self.assertAlmostEqual(self.mixin.resistances.shield.thermal, 0.9)
        self.assertAlmostEqual(self.mixin.resistances.shield.kinetic, 0.89)
        self.assertAlmostEqual(self.mixin.resistances.shield.explosive, 0.88)

    def test_volatility(self):
        self.mixin.attributes[Attribute.em_damage_resonance] = 0.01
        self.mixin.attributes[Attribute.thermal_damage_resonance] = 0.02
        self.mixin.attributes[Attribute.kinetic_damage_resonance] = 0.03
        self.mixin.attributes[Attribute.explosive_damage_resonance] = 0.04
        self.mixin.attributes[Attribute.armor_em_damage_resonance] = 0.05
        self.mixin.attributes[Attribute.armor_thermal_damage_resonance] = 0.06
        self.mixin.attributes[Attribute.armor_kinetic_damage_resonance] = 0.07
        self.mixin.attributes[Attribute.armor_explosive_damage_resonance] = 0.08
        self.mixin.attributes[Attribute.shield_em_damage_resonance] = 0.09
        self.mixin.attributes[Attribute.shield_thermal_damage_resonance] = 0.1
        self.mixin.attributes[Attribute.shield_kinetic_damage_resonance] = 0.11
        self.mixin.attributes[Attribute.shield_explosive_damage_resonance] = 0.12
        self.assertAlmostEqual(self.mixin.resistances.hull.em, 0.99)
        self.assertAlmostEqual(self.mixin.resistances.hull.thermal, 0.98)
        self.assertAlmostEqual(self.mixin.resistances.hull.kinetic, 0.97)
        self.assertAlmostEqual(self.mixin.resistances.hull.explosive, 0.96)
        self.assertAlmostEqual(self.mixin.resistances.armor.em, 0.95)
        self.assertAlmostEqual(self.mixin.resistances.armor.thermal, 0.94)
        self.assertAlmostEqual(self.mixin.resistances.armor.kinetic, 0.93)
        self.assertAlmostEqual(self.mixin.resistances.armor.explosive, 0.92)
        self.assertAlmostEqual(self.mixin.resistances.shield.em, 0.91)
        self.assertAlmostEqual(self.mixin.resistances.shield.thermal, 0.9)
        self.assertAlmostEqual(self.mixin.resistances.shield.kinetic, 0.89)
        self.assertAlmostEqual(self.mixin.resistances.shield.explosive, 0.88)
        self.mixin._clear_volatile_attrs()
        self.mixin.attributes[Attribute.em_damage_resonance] = 0.11
        self.mixin.attributes[Attribute.thermal_damage_resonance] = 0.12
        self.mixin.attributes[Attribute.kinetic_damage_resonance] = 0.13
        self.mixin.attributes[Attribute.explosive_damage_resonance] = 0.14
        self.mixin.attributes[Attribute.armor_em_damage_resonance] = 0.15
        self.mixin.attributes[Attribute.armor_thermal_damage_resonance] = 0.16
        self.mixin.attributes[Attribute.armor_kinetic_damage_resonance] = 0.17
        self.mixin.attributes[Attribute.armor_explosive_damage_resonance] = 0.18
        self.mixin.attributes[Attribute.shield_em_damage_resonance] = 0.19
        self.mixin.attributes[Attribute.shield_thermal_damage_resonance] = 0.2
        self.mixin.attributes[Attribute.shield_kinetic_damage_resonance] = 0.21
        self.mixin.attributes[Attribute.shield_explosive_damage_resonance] = 0.22
        self.assertAlmostEqual(self.mixin.resistances.hull.em, 0.89)
        self.assertAlmostEqual(self.mixin.resistances.hull.thermal, 0.88)
        self.assertAlmostEqual(self.mixin.resistances.hull.kinetic, 0.87)
        self.assertAlmostEqual(self.mixin.resistances.hull.explosive, 0.86)
        self.assertAlmostEqual(self.mixin.resistances.armor.em, 0.85)
        self.assertAlmostEqual(self.mixin.resistances.armor.thermal, 0.84)
        self.assertAlmostEqual(self.mixin.resistances.armor.kinetic, 0.83)
        self.assertAlmostEqual(self.mixin.resistances.armor.explosive, 0.82)
        self.assertAlmostEqual(self.mixin.resistances.shield.em, 0.81)
        self.assertAlmostEqual(self.mixin.resistances.shield.thermal, 0.8)
        self.assertAlmostEqual(self.mixin.resistances.shield.kinetic, 0.79)
        self.assertAlmostEqual(self.mixin.resistances.shield.explosive, 0.78)
