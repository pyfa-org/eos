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


class TestHolderMixinDamageBomb(FitTestCase):

    def setUp(self):
        FitTestCase.setUp(self)
        mixin = DamageDealerMixin(type_id=None)
        mixin.item = Mock()
        mixin.item.default_effect.id = Effect.use_missiles
        mixin.item.default_effect._state = State.active
        mixin.attributes = {}
        mixin.state = State.active
        mixin.cycle_time = 0.5
        mixin.reactivation_delay = None
        mixin.charge = Mock()
        mixin.charge.item.default_effect.id = Effect.bomb_launching
        mixin.charge.attributes = {}
        mixin.fully_charged_cycles_max = None
        mixin.reload_time = None
        self.mixin = mixin

    def test_nominal_volley(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        volley = mixin.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 5.2)
        self.assertAlmostEqual(volley.thermal, 6.3)
        self.assertAlmostEqual(volley.kinetic, 7.4)
        self.assertAlmostEqual(volley.explosive, 8.5)
        self.assertAlmostEqual(volley.total, 27.4)

    def test_nominal_volley_effective(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        profile = Mock(em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = mixin.get_nominal_volley(target_resistances=profile)
        self.assertAlmostEqual(volley.em, 4.16)
        self.assertAlmostEqual(volley.thermal, 5.04)
        self.assertAlmostEqual(volley.kinetic, 1.48)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 10.68)

    def test_nominal_volley_multiplier(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        volley = mixin.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 5.2)
        self.assertAlmostEqual(volley.thermal, 6.3)
        self.assertAlmostEqual(volley.kinetic, 7.4)
        self.assertAlmostEqual(volley.explosive, 8.5)
        self.assertAlmostEqual(volley.total, 27.4)

    def test_nominal_volley_no_attrib_single(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        volley = mixin.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 5.2)
        self.assertAlmostEqual(volley.thermal, 0)
        self.assertAlmostEqual(volley.kinetic, 7.4)
        self.assertAlmostEqual(volley.explosive, 8.5)
        self.assertAlmostEqual(volley.total, 21.1)

    def test_nominal_volley_no_attrib_all(self):
        mixin = self.mixin
        volley = mixin.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 0)
        self.assertAlmostEqual(volley.thermal, 0)
        self.assertAlmostEqual(volley.kinetic, 0)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 0)

    def test_nominal_volley_insufficient_state(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        mixin.state = State.online
        volley = mixin.get_nominal_volley()
        self.assertIsNone(volley)

    def test_nominal_volley_no_charge(self):
        mixin = self.mixin
        mixin.charge = None
        volley = mixin.get_nominal_volley()
        self.assertIsNone(volley)

    def test_nominal_volley_no_charged_cycles(self):
        mixin = self.mixin
        mixin.fully_charged_cycles_max = 0
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        volley = mixin.get_nominal_volley()
        self.assertIsNone(volley)

    def test_nominal_volley_cache(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        volley = mixin.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 5.2)
        self.assertAlmostEqual(volley.thermal, 6.3)
        self.assertAlmostEqual(volley.kinetic, 7.4)
        self.assertAlmostEqual(volley.explosive, 8.5)
        self.assertAlmostEqual(volley.total, 27.4)
        profile = Mock(em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = mixin.get_nominal_volley(target_resistances=profile)
        self.assertAlmostEqual(volley.em, 4.16)
        self.assertAlmostEqual(volley.thermal, 5.04)
        self.assertAlmostEqual(volley.kinetic, 1.48)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 10.68)
        mixin.charge.attributes[Attribute.em_damage] = 52
        mixin.charge.attributes[Attribute.thermal_damage] = 63
        mixin.charge.attributes[Attribute.kinetic_damage] = 74
        mixin.charge.attributes[Attribute.explosive_damage] = 85
        volley = mixin.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 5.2)
        self.assertAlmostEqual(volley.thermal, 6.3)
        self.assertAlmostEqual(volley.kinetic, 7.4)
        self.assertAlmostEqual(volley.explosive, 8.5)
        self.assertAlmostEqual(volley.total, 27.4)
        profile = Mock(em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = mixin.get_nominal_volley(target_resistances=profile)
        self.assertAlmostEqual(volley.em, 4.16)
        self.assertAlmostEqual(volley.thermal, 5.04)
        self.assertAlmostEqual(volley.kinetic, 1.48)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 10.68)

    def test_nominal_volley_volatility(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        volley = mixin.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 5.2)
        self.assertAlmostEqual(volley.thermal, 6.3)
        self.assertAlmostEqual(volley.kinetic, 7.4)
        self.assertAlmostEqual(volley.explosive, 8.5)
        self.assertAlmostEqual(volley.total, 27.4)
        profile = Mock(em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = mixin.get_nominal_volley(target_resistances=profile)
        self.assertAlmostEqual(volley.em, 4.16)
        self.assertAlmostEqual(volley.thermal, 5.04)
        self.assertAlmostEqual(volley.kinetic, 1.48)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 10.68)
        mixin._clear_volatile_attrs()
        mixin.charge.attributes[Attribute.em_damage] = 52
        mixin.charge.attributes[Attribute.thermal_damage] = 63
        mixin.charge.attributes[Attribute.kinetic_damage] = 74
        mixin.charge.attributes[Attribute.explosive_damage] = 85
        volley = mixin.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 52)
        self.assertAlmostEqual(volley.thermal, 63)
        self.assertAlmostEqual(volley.kinetic, 74)
        self.assertAlmostEqual(volley.explosive, 85)
        self.assertAlmostEqual(volley.total, 274)
        profile = Mock(em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = mixin.get_nominal_volley(target_resistances=profile)
        self.assertAlmostEqual(volley.em, 41.6)
        self.assertAlmostEqual(volley.thermal, 50.4)
        self.assertAlmostEqual(volley.kinetic, 14.8)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 106.8)

    def test_nominal_dps(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        dps = mixin.get_nominal_dps(reload=False)
        self.assertAlmostEqual(dps.em, 10.4)
        self.assertAlmostEqual(dps.thermal, 12.6)
        self.assertAlmostEqual(dps.kinetic, 14.8)
        self.assertAlmostEqual(dps.explosive, 17)
        self.assertAlmostEqual(dps.total, 54.8)

    def test_nominal_dps_reload(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        dps = mixin.get_nominal_dps(reload=True)
        self.assertAlmostEqual(dps.em, 10.4)
        self.assertAlmostEqual(dps.thermal, 12.6)
        self.assertAlmostEqual(dps.kinetic, 14.8)
        self.assertAlmostEqual(dps.explosive, 17)
        self.assertAlmostEqual(dps.total, 54.8)

    def test_nominal_dps_reactivation(self):
        mixin = self.mixin
        mixin.reactivation_delay = 1.5
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        dps = mixin.get_nominal_dps(reload=False)
        self.assertAlmostEqual(dps.em, 2.6)
        self.assertAlmostEqual(dps.thermal, 3.15)
        self.assertAlmostEqual(dps.kinetic, 3.7)
        self.assertAlmostEqual(dps.explosive, 4.25)
        self.assertAlmostEqual(dps.total, 13.7)

    def test_nominal_dps_reactivation_reload(self):
        mixin = self.mixin
        mixin.reactivation_delay = 1.5
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        dps = mixin.get_nominal_dps(reload=True)
        self.assertAlmostEqual(dps.em, 2.6)
        self.assertAlmostEqual(dps.thermal, 3.15)
        self.assertAlmostEqual(dps.kinetic, 3.7)
        self.assertAlmostEqual(dps.explosive, 4.25)
        self.assertAlmostEqual(dps.total, 13.7)

    def test_nominal_dps_limited_charges(self):
        mixin = self.mixin
        mixin.fully_charged_cycles_max = 10
        mixin.reload_time = 5
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        dps = mixin.get_nominal_dps(reload=False)
        self.assertAlmostEqual(dps.em, 10.4)
        self.assertAlmostEqual(dps.thermal, 12.6)
        self.assertAlmostEqual(dps.kinetic, 14.8)
        self.assertAlmostEqual(dps.explosive, 17.0)
        self.assertAlmostEqual(dps.total, 54.8)

    def test_nominal_dps_limited_charges_reload(self):
        mixin = self.mixin
        mixin.fully_charged_cycles_max = 10
        mixin.reload_time = 5
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        dps = mixin.get_nominal_dps(reload=True)
        self.assertAlmostEqual(dps.em, 5.2)
        self.assertAlmostEqual(dps.thermal, 6.3)
        self.assertAlmostEqual(dps.kinetic, 7.4)
        self.assertAlmostEqual(dps.explosive, 8.5)
        self.assertAlmostEqual(dps.total, 27.4)

    def test_nominal_dps_reactivation_limited_charges_partial(self):
        mixin = self.mixin
        mixin.reactivation_delay = 1.5
        mixin.fully_charged_cycles_max = 10
        mixin.reload_time = 6.5
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        dps = mixin.get_nominal_dps(reload=True)
        self.assertAlmostEqual(dps.em, 2.08)
        self.assertAlmostEqual(dps.thermal, 2.52)
        self.assertAlmostEqual(dps.kinetic, 2.96)
        self.assertAlmostEqual(dps.explosive, 3.4)
        self.assertAlmostEqual(dps.total, 10.96)

    def test_nominal_dps_reactivation_limited_charges_full(self):
        mixin = self.mixin
        mixin.reactivation_delay = 19.5
        mixin.fully_charged_cycles_max = 10
        mixin.reload_time = 6.5
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        dps = mixin.get_nominal_dps(reload=True)
        self.assertAlmostEqual(dps.em, 0.26)
        self.assertAlmostEqual(dps.thermal, 0.315)
        self.assertAlmostEqual(dps.kinetic, 0.37)
        self.assertAlmostEqual(dps.explosive, 0.425)
        self.assertAlmostEqual(dps.total, 1.37)

    def test_nominal_dps_effective(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        profile = Mock(em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        dps = mixin.get_nominal_volley(target_resistances=profile)
        self.assertAlmostEqual(dps.em, 4.16)
        self.assertAlmostEqual(dps.thermal, 5.04)
        self.assertAlmostEqual(dps.kinetic, 1.48)
        self.assertAlmostEqual(dps.explosive, 0)
        self.assertAlmostEqual(dps.total, 10.68)

    def test_nominal_dps_none_volley(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        mixin.state = State.online
        dps = mixin.get_nominal_dps()
        self.assertIsNone(dps)
