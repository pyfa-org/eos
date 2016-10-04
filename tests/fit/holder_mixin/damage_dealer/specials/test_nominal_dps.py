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


class TestHolderMixinDamageSpecialsNominalDps(FitTestCase):

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

    def test_effective(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        profile = Mock(em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        dps = mixin.get_nominal_volley(target_resistances=profile)
        self.assertAlmostEqual(dps.em, 22.88)
        self.assertAlmostEqual(dps.thermal, 27.72)
        self.assertAlmostEqual(dps.kinetic, 8.14)
        self.assertAlmostEqual(dps.explosive, 0)
        self.assertAlmostEqual(dps.total, 58.74)

    def test_reactivation_limited_charges_partial(self):
        mixin = self.mixin
        mixin.reactivation_delay = 1.5
        mixin.fully_charged_cycles_max = 10
        mixin.reload_time = 6.5
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        dps = mixin.get_nominal_dps(reload=True)
        self.assertAlmostEqual(dps.em, 11.44)
        self.assertAlmostEqual(dps.thermal, 13.86)
        self.assertAlmostEqual(dps.kinetic, 16.28)
        self.assertAlmostEqual(dps.explosive, 18.7)
        self.assertAlmostEqual(dps.total, 60.28)

    def test_reactivation_limited_charges_full(self):
        mixin = self.mixin
        mixin.reactivation_delay = 19.5
        mixin.fully_charged_cycles_max = 10
        mixin.reload_time = 6.5
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        dps = mixin.get_nominal_dps(reload=True)
        self.assertAlmostEqual(dps.em, 1.43)
        self.assertAlmostEqual(dps.thermal, 1.7325)
        self.assertAlmostEqual(dps.kinetic, 2.035)
        self.assertAlmostEqual(dps.explosive, 2.3375)
        self.assertAlmostEqual(dps.total, 7.535)

    def test_reactivation_no_attrib_single_em(self):
        mixin = self.mixin
        mixin.reactivation_delay = 1.5
        mixin.fully_charged_cycles_max = 10
        mixin.reload_time = 6.5
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        dps = mixin.get_nominal_dps(reload=True)
        self.assertIsNone(dps.em)
        self.assertAlmostEqual(dps.thermal, 13.86)
        self.assertAlmostEqual(dps.kinetic, 16.28)
        self.assertAlmostEqual(dps.explosive, 18.7)
        self.assertAlmostEqual(dps.total, 48.84)

    def test_reactivation_no_attrib_single_therm(self):
        mixin = self.mixin
        mixin.reactivation_delay = 1.5
        mixin.fully_charged_cycles_max = 10
        mixin.reload_time = 6.5
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        dps = mixin.get_nominal_dps(reload=True)
        self.assertAlmostEqual(dps.em, 11.44)
        self.assertIsNone(dps.thermal)
        self.assertAlmostEqual(dps.kinetic, 16.28)
        self.assertAlmostEqual(dps.explosive, 18.7)
        self.assertAlmostEqual(dps.total, 46.42)

    def test_reactivation_no_attrib_single_kin(self):
        mixin = self.mixin
        mixin.reactivation_delay = 1.5
        mixin.fully_charged_cycles_max = 10
        mixin.reload_time = 6.5
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        dps = mixin.get_nominal_dps(reload=True)
        self.assertAlmostEqual(dps.em, 11.44)
        self.assertAlmostEqual(dps.thermal, 13.86)
        self.assertIsNone(dps.kinetic)
        self.assertAlmostEqual(dps.explosive, 18.7)
        self.assertAlmostEqual(dps.total, 44)

    def test_reactivation_no_attrib_single_expl(self):
        mixin = self.mixin
        mixin.reactivation_delay = 1.5
        mixin.fully_charged_cycles_max = 10
        mixin.reload_time = 6.5
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        dps = mixin.get_nominal_dps(reload=True)
        self.assertAlmostEqual(dps.em, 11.44)
        self.assertAlmostEqual(dps.thermal, 13.86)
        self.assertAlmostEqual(dps.kinetic, 16.28)
        self.assertIsNone(dps.explosive)
        self.assertAlmostEqual(dps.total, 41.58)

    def test_reactivation_no_attrib_all(self):
        mixin = self.mixin
        mixin.reactivation_delay = 1.5
        mixin.fully_charged_cycles_max = 10
        mixin.reload_time = 6.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        dps = mixin.get_nominal_dps(reload=True)
        self.assertIsNone(dps.em)
        self.assertIsNone(dps.thermal)
        self.assertIsNone(dps.kinetic)
        self.assertIsNone(dps.explosive)
        self.assertIsNone(dps.total)

    def test_reactivation_single_zero_attrib_em(self):
        mixin = self.mixin
        mixin.reactivation_delay = 1.5
        mixin.fully_charged_cycles_max = 10
        mixin.reload_time = 6.5
        mixin.charge.attributes[Attribute.em_damage] = 0
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        dps = mixin.get_nominal_dps(reload=True)
        self.assertAlmostEqual(dps.em, 0)
        self.assertIsNone(dps.thermal)
        self.assertIsNone(dps.kinetic)
        self.assertIsNone(dps.explosive)
        self.assertAlmostEqual(dps.total, 0)

    def test_reactivation_single_zero_attrib_therm(self):
        mixin = self.mixin
        mixin.reactivation_delay = 1.5
        mixin.fully_charged_cycles_max = 10
        mixin.reload_time = 6.5
        mixin.charge.attributes[Attribute.thermal_damage] = 0
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        dps = mixin.get_nominal_dps(reload=True)
        self.assertIsNone(dps.em)
        self.assertAlmostEqual(dps.thermal, 0)
        self.assertIsNone(dps.kinetic)
        self.assertIsNone(dps.explosive)
        self.assertAlmostEqual(dps.total, 0)

    def test_reactivation_single_zero_attrib_kin(self):
        mixin = self.mixin
        mixin.reactivation_delay = 1.5
        mixin.fully_charged_cycles_max = 10
        mixin.reload_time = 6.5
        mixin.charge.attributes[Attribute.kinetic_damage] = 0
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        dps = mixin.get_nominal_dps(reload=True)
        self.assertIsNone(dps.em)
        self.assertIsNone(dps.thermal)
        self.assertAlmostEqual(dps.kinetic, 0)
        self.assertIsNone(dps.explosive)
        self.assertAlmostEqual(dps.total, 0)

    def test_reactivation_single_zero_attrib_expl(self):
        mixin = self.mixin
        mixin.reactivation_delay = 1.5
        mixin.fully_charged_cycles_max = 10
        mixin.reload_time = 6.5
        mixin.charge.attributes[Attribute.explosive_damage] = 0
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        dps = mixin.get_nominal_dps(reload=True)
        self.assertIsNone(dps.em)
        self.assertIsNone(dps.thermal)
        self.assertIsNone(dps.kinetic)
        self.assertAlmostEqual(dps.explosive, 0)
        self.assertAlmostEqual(dps.total, 0)

    def test_volley_nones_all(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        mixin.state = State.online
        dps = mixin.get_nominal_dps()
        self.assertIsNone(dps.em)
        self.assertIsNone(dps.thermal)
        self.assertIsNone(dps.kinetic)
        self.assertIsNone(dps.explosive)
        self.assertIsNone(dps.total)
