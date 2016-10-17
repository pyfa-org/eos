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


from unittest.mock import Mock

from eos.const.eos import State
from eos.const.eve import Attribute, Effect
from eos.fit.holder.mixin.damage_dealer import DamageDealerMixin
from tests.fit.fit_testcase import FitTestCase


class TestHolderMixinDamageSpecialsNominalVolley(FitTestCase):

    def setUp(self):
        super().setUp()
        mixin = DamageDealerMixin()
        mixin.item = Mock()
        mixin.item.default_effect.id = Effect.projectile_fired
        mixin.item.default_effect._state = State.active
        mixin.attributes = {}
        mixin.state = State.active
        mixin.cycle_time = 0.5
        mixin.reactivation_delay = None
        mixin.charge = Mock()
        mixin.charge.attributes = {}
        mixin.fully_charged_cycles_max = None
        mixin.reload_time = None
        self.mixin = mixin

    def test_no_attrib_single_em(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        volley = mixin.get_nominal_volley()
        self.assertIsNone(volley.em)
        self.assertAlmostEqual(volley.thermal, 34.65)
        self.assertAlmostEqual(volley.kinetic, 40.7)
        self.assertAlmostEqual(volley.explosive, 46.75)
        self.assertAlmostEqual(volley.total, 122.1)

    def test_attrib_single_therm(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        volley = mixin.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 28.6)
        self.assertIsNone(volley.thermal)
        self.assertAlmostEqual(volley.kinetic, 40.7)
        self.assertAlmostEqual(volley.explosive, 46.75)
        self.assertAlmostEqual(volley.total, 116.05)

    def test_no_attrib_single_kin(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        volley = mixin.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 28.6)
        self.assertAlmostEqual(volley.thermal, 34.65)
        self.assertIsNone(volley.kinetic)
        self.assertAlmostEqual(volley.explosive, 46.75)
        self.assertAlmostEqual(volley.total, 110)

    def test_no_attrib_single_expl(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        volley = mixin.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 28.6)
        self.assertAlmostEqual(volley.thermal, 34.65)
        self.assertAlmostEqual(volley.kinetic, 40.7)
        self.assertIsNone(volley.explosive)
        self.assertAlmostEqual(volley.total, 103.95)

    def test_no_attrib_all(self):
        mixin = self.mixin
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        volley = mixin.get_nominal_volley()
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertIsNone(volley.total)

    def test_single_zero_attrib_em(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.em_damage] = 0
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        volley = mixin.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 0)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertAlmostEqual(volley.total, 0)

    def test_single_zero_attrib_therm(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.thermal_damage] = 0
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        volley = mixin.get_nominal_volley()
        self.assertIsNone(volley.em)
        self.assertAlmostEqual(volley.thermal, 0)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertAlmostEqual(volley.total, 0)

    def test_single_zero_attrib_kin(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.kinetic_damage] = 0
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        volley = mixin.get_nominal_volley()
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertAlmostEqual(volley.kinetic, 0)
        self.assertIsNone(volley.explosive)
        self.assertAlmostEqual(volley.total, 0)

    def test_single_zero_attrib_expl(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.explosive_damage] = 0
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        volley = mixin.get_nominal_volley()
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 0)

    def test_effective(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        profile = Mock(em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = mixin.get_nominal_volley(target_resistances=profile)
        self.assertAlmostEqual(volley.em, 22.88)
        self.assertAlmostEqual(volley.thermal, 27.72)
        self.assertAlmostEqual(volley.kinetic, 8.14)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 58.74)

    def test_effective_no_attrib_single_em(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        profile = Mock(em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = mixin.get_nominal_volley(target_resistances=profile)
        self.assertIsNone(volley.em)
        self.assertAlmostEqual(volley.thermal, 27.72)
        self.assertAlmostEqual(volley.kinetic, 8.14)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 35.86)

    def test_effective_no_attrib_single_therm(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        profile = Mock(em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = mixin.get_nominal_volley(target_resistances=profile)
        self.assertAlmostEqual(volley.em, 22.88)
        self.assertIsNone(volley.thermal)
        self.assertAlmostEqual(volley.kinetic, 8.14)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 31.02)

    def test_effective_no_attrib_single_kin(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        profile = Mock(em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = mixin.get_nominal_volley(target_resistances=profile)
        self.assertAlmostEqual(volley.em, 22.88)
        self.assertAlmostEqual(volley.thermal, 27.72)
        self.assertIsNone(volley.kinetic)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 50.6)

    def test_effective_no_attrib_single_expl(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        profile = Mock(em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = mixin.get_nominal_volley(target_resistances=profile)
        self.assertAlmostEqual(volley.em, 22.88)
        self.assertAlmostEqual(volley.thermal, 27.72)
        self.assertAlmostEqual(volley.kinetic, 8.14)
        self.assertIsNone(volley.explosive)
        self.assertAlmostEqual(volley.total, 58.74)

    def test_effective_no_attrib_all(self):
        mixin = self.mixin
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        profile = Mock(em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = mixin.get_nominal_volley(target_resistances=profile)
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertIsNone(volley.total)

    def test_effective_single_zero_attrib_em(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.em_damage] = 0
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        profile = Mock(em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = mixin.get_nominal_volley(target_resistances=profile)
        self.assertAlmostEqual(volley.em, 0)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertAlmostEqual(volley.total, 0)

    def test_effective_single_zero_attrib_therm(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.thermal_damage] = 0
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        profile = Mock(em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = mixin.get_nominal_volley(target_resistances=profile)
        self.assertIsNone(volley.em)
        self.assertAlmostEqual(volley.thermal, 0)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertAlmostEqual(volley.total, 0)

    def test_effective_single_zero_attrib_kin(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.kinetic_damage] = 0
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        profile = Mock(em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = mixin.get_nominal_volley(target_resistances=profile)
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertAlmostEqual(volley.kinetic, 0)
        self.assertIsNone(volley.explosive)
        self.assertAlmostEqual(volley.total, 0)

    def test_effective_single_zero_attrib_expl(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.explosive_damage] = 0
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        profile = Mock(em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = mixin.get_nominal_volley(target_resistances=profile)
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 0)

    def test_no_charged_cycles(self):
        mixin = self.mixin
        mixin.fully_charged_cycles_max = 0
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        volley = mixin.get_nominal_volley()
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertIsNone(volley.total)
