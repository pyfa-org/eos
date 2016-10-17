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


class TestHolderMixinDamageBombNominalDps(FitTestCase):

    def setUp(self):
        super().setUp()
        mixin = DamageDealerMixin()
        mixin.item = Mock()
        mixin.item.default_effect.id = Effect.use_missiles
        mixin.item.default_effect._state = State.active
        mixin.attributes = {}
        mixin.state = State.active
        mixin.cycle_time = 0.5
        mixin.reactivation_delay = 1.5
        mixin.charge = Mock()
        mixin.charge.item.default_effect.id = Effect.bomb_launching
        mixin.charge.attributes = {}
        mixin.fully_charged_cycles_max = 2
        mixin.reload_time = 10
        self.mixin = mixin

    def test_no_reload(self):
        mixin = self.mixin
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

    def test_reload(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        dps = mixin.get_nominal_dps(reload=True)
        self.assertAlmostEqual(dps.em, 0.832)
        self.assertAlmostEqual(dps.thermal, 1.008)
        self.assertAlmostEqual(dps.kinetic, 1.184)
        self.assertAlmostEqual(dps.explosive, 1.36)
        self.assertAlmostEqual(dps.total, 4.384)
