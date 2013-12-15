#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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
#===============================================================================


from unittest.mock import Mock

from eos.const.eos import State
from eos.const.eve import Attribute, Effect
from eos.fit.holder.mixin.damage_dealer import DamageDealerMixin
from eos.tests.fit.fit_testcase import FitTestCase


class TestHolderMixinDamageFighterBomber(FitTestCase):

    def setUp(self):
        FitTestCase.setUp(self)
        mixin = DamageDealerMixin()
        mixin.item = Mock()
        mixin.item.default_effect.id = Effect.fighter_missile
        mixin.item.default_effect._state = State.active
        mixin.attributes = {}
        mixin.state = State.active
        mixin.cycle_time = 0.5
        self.mixin = mixin

    def test_nominal_volley(self):
        mixin = self.mixin
        mixin.attributes[Attribute.em_damage] = 5.2
        mixin.attributes[Attribute.thermal_damage] = 6.3
        mixin.attributes[Attribute.kinetic_damage] = 7.4
        mixin.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        volley = mixin.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 28.6)
        self.assertAlmostEqual(volley.thermal, 34.65)
        self.assertAlmostEqual(volley.kinetic, 40.7)
        self.assertAlmostEqual(volley.explosive, 46.75)
        self.assertAlmostEqual(volley.total, 150.7)

    def test_nominal_volley_effective(self):
        mixin = self.mixin
        mixin.attributes[Attribute.em_damage] = 5.2
        mixin.attributes[Attribute.thermal_damage] = 6.3
        mixin.attributes[Attribute.kinetic_damage] = 7.4
        mixin.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        profile = Mock(em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = mixin.get_nominal_volley(target_resistances=profile)
        self.assertAlmostEqual(volley.em, 22.88)
        self.assertAlmostEqual(volley.thermal, 27.72)
        self.assertAlmostEqual(volley.kinetic, 8.14)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 58.74)

    def test_nominal_volley_no_multiplier(self):
        mixin = self.mixin
        mixin.attributes[Attribute.em_damage] = 5.2
        mixin.attributes[Attribute.thermal_damage] = 6.3
        mixin.attributes[Attribute.kinetic_damage] = 7.4
        mixin.attributes[Attribute.explosive_damage] = 8.5
        volley = mixin.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 5.2)
        self.assertAlmostEqual(volley.thermal, 6.3)
        self.assertAlmostEqual(volley.kinetic, 7.4)
        self.assertAlmostEqual(volley.explosive, 8.5)
        self.assertAlmostEqual(volley.total, 27.4)

    def test_nominal_volley_no_attrib_single(self):
        mixin = self.mixin
        mixin.attributes[Attribute.em_damage] = 5.2
        mixin.attributes[Attribute.kinetic_damage] = 7.4
        mixin.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        volley = mixin.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 28.6)
        self.assertAlmostEqual(volley.thermal, 0)
        self.assertAlmostEqual(volley.kinetic, 40.7)
        self.assertAlmostEqual(volley.explosive, 46.75)
        self.assertAlmostEqual(volley.total, 116.05)

    def test_nominal_volley_no_attrib_all(self):
        mixin = self.mixin
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        volley = mixin.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 0)
        self.assertAlmostEqual(volley.thermal, 0)
        self.assertAlmostEqual(volley.kinetic, 0)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 0)

    def test_nominal_volley_insufficient_state(self):
        mixin = self.mixin
        mixin.attributes[Attribute.em_damage] = 5.2
        mixin.attributes[Attribute.thermal_damage] = 6.3
        mixin.attributes[Attribute.kinetic_damage] = 7.4
        mixin.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        mixin.state = State.online
        volley = mixin.get_nominal_volley()
        self.assertIsNone(volley)

    def test_nominal_volley_charge_attrs(self):
        mixin = self.mixin
        mixin.charge = Mock()
        mixin.charge.attributes = {}
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        volley = mixin.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 0)
        self.assertAlmostEqual(volley.thermal, 0)
        self.assertAlmostEqual(volley.kinetic, 0)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 0)

    def test_nominal_volley_cache(self):
        mixin = self.mixin
        mixin.attributes[Attribute.em_damage] = 5.2
        mixin.attributes[Attribute.thermal_damage] = 6.3
        mixin.attributes[Attribute.kinetic_damage] = 7.4
        mixin.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        volley = mixin.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 28.6)
        self.assertAlmostEqual(volley.thermal, 34.65)
        self.assertAlmostEqual(volley.kinetic, 40.7)
        self.assertAlmostEqual(volley.explosive, 46.75)
        self.assertAlmostEqual(volley.total, 150.7)
        profile = Mock(em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = mixin.get_nominal_volley(target_resistances=profile)
        self.assertAlmostEqual(volley.em, 22.88)
        self.assertAlmostEqual(volley.thermal, 27.72)
        self.assertAlmostEqual(volley.kinetic, 8.14)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 58.74)
        mixin.attributes[Attribute.em_damage] = 52
        mixin.attributes[Attribute.thermal_damage] = 63
        mixin.attributes[Attribute.kinetic_damage] = 74
        mixin.attributes[Attribute.explosive_damage] = 85
        mixin.attributes[Attribute.damage_multiplier] = 55
        volley = mixin.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 28.6)
        self.assertAlmostEqual(volley.thermal, 34.65)
        self.assertAlmostEqual(volley.kinetic, 40.7)
        self.assertAlmostEqual(volley.explosive, 46.75)
        self.assertAlmostEqual(volley.total, 150.7)
        profile = Mock(em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = mixin.get_nominal_volley(target_resistances=profile)
        self.assertAlmostEqual(volley.em, 22.88)
        self.assertAlmostEqual(volley.thermal, 27.72)
        self.assertAlmostEqual(volley.kinetic, 8.14)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 58.74)

    def test_nominal_volley_volatility(self):
        mixin = self.mixin
        mixin.attributes[Attribute.em_damage] = 5.2
        mixin.attributes[Attribute.thermal_damage] = 6.3
        mixin.attributes[Attribute.kinetic_damage] = 7.4
        mixin.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        volley = mixin.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 28.6)
        self.assertAlmostEqual(volley.thermal, 34.65)
        self.assertAlmostEqual(volley.kinetic, 40.7)
        self.assertAlmostEqual(volley.explosive, 46.75)
        self.assertAlmostEqual(volley.total, 150.7)
        profile = Mock(em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = mixin.get_nominal_volley(target_resistances=profile)
        self.assertAlmostEqual(volley.em, 22.88)
        self.assertAlmostEqual(volley.thermal, 27.72)
        self.assertAlmostEqual(volley.kinetic, 8.14)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 58.74)
        mixin._clear_volatile_attrs()
        mixin.attributes[Attribute.em_damage] = 52
        mixin.attributes[Attribute.thermal_damage] = 63
        mixin.attributes[Attribute.kinetic_damage] = 74
        mixin.attributes[Attribute.explosive_damage] = 85
        mixin.attributes[Attribute.damage_multiplier] = 55
        volley = mixin.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 2860)
        self.assertAlmostEqual(volley.thermal, 3465)
        self.assertAlmostEqual(volley.kinetic, 4070)
        self.assertAlmostEqual(volley.explosive, 4675)
        self.assertAlmostEqual(volley.total, 15070)
        profile = Mock(em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = mixin.get_nominal_volley(target_resistances=profile)
        self.assertAlmostEqual(volley.em, 2288)
        self.assertAlmostEqual(volley.thermal, 2772)
        self.assertAlmostEqual(volley.kinetic, 814)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 5874)

    def test_nominal_dps(self):
        mixin = self.mixin
        mixin.attributes[Attribute.em_damage] = 5.2
        mixin.attributes[Attribute.thermal_damage] = 6.3
        mixin.attributes[Attribute.kinetic_damage] = 7.4
        mixin.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        dps = mixin.get_nominal_dps(reload=False)
        self.assertAlmostEqual(dps.em, 57.2)
        self.assertAlmostEqual(dps.thermal, 69.3)
        self.assertAlmostEqual(dps.kinetic, 81.4)
        self.assertAlmostEqual(dps.explosive, 93.5)
        self.assertAlmostEqual(dps.total, 301.4)

    def test_nominal_dps_reload(self):
        mixin = self.mixin
        mixin.attributes[Attribute.em_damage] = 5.2
        mixin.attributes[Attribute.thermal_damage] = 6.3
        mixin.attributes[Attribute.kinetic_damage] = 7.4
        mixin.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        dps = mixin.get_nominal_dps(reload=True)
        self.assertAlmostEqual(dps.em, 57.2)
        self.assertAlmostEqual(dps.thermal, 69.3)
        self.assertAlmostEqual(dps.kinetic, 81.4)
        self.assertAlmostEqual(dps.explosive, 93.5)
        self.assertAlmostEqual(dps.total, 301.4)

    def test_nominal_dps_effective(self):
        mixin = self.mixin
        mixin.attributes[Attribute.em_damage] = 5.2
        mixin.attributes[Attribute.thermal_damage] = 6.3
        mixin.attributes[Attribute.kinetic_damage] = 7.4
        mixin.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        profile = Mock(em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        dps = mixin.get_nominal_volley(target_resistances=profile)
        self.assertAlmostEqual(dps.em, 22.88)
        self.assertAlmostEqual(dps.thermal, 27.72)
        self.assertAlmostEqual(dps.kinetic, 8.14)
        self.assertAlmostEqual(dps.explosive, 0)
        self.assertAlmostEqual(dps.total, 58.74)

    def test_nominal_dps_none_volley(self):
        mixin = self.mixin
        mixin.attributes[Attribute.em_damage] = 5.2
        mixin.attributes[Attribute.thermal_damage] = 6.3
        mixin.attributes[Attribute.kinetic_damage] = 7.4
        mixin.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        mixin.state = State.online
        dps = mixin.get_nominal_dps()
        self.assertIsNone(dps)