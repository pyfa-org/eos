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


class TestHolderMixinDamageTurretNominalDps(FitTestCase):

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
        mixin.fully_charged_cycles_max = 10
        mixin.reload_time = 5
        self.mixin = mixin

    def test_no_reload(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        dps = mixin.get_nominal_dps(reload=False)
        self.assertAlmostEqual(dps.em, 57.2)
        self.assertAlmostEqual(dps.thermal, 69.3)
        self.assertAlmostEqual(dps.kinetic, 81.4)
        self.assertAlmostEqual(dps.explosive, 93.5)
        self.assertAlmostEqual(dps.total, 301.4)

    def test_reload(self):
        mixin = self.mixin
        mixin.charge.attributes[Attribute.em_damage] = 5.2
        mixin.charge.attributes[Attribute.thermal_damage] = 6.3
        mixin.charge.attributes[Attribute.kinetic_damage] = 7.4
        mixin.charge.attributes[Attribute.explosive_damage] = 8.5
        mixin.attributes[Attribute.damage_multiplier] = 5.5
        dps = mixin.get_nominal_dps(reload=True)
        self.assertAlmostEqual(dps.em, 28.6)
        self.assertAlmostEqual(dps.thermal, 34.65)
        self.assertAlmostEqual(dps.kinetic, 40.7)
        self.assertAlmostEqual(dps.explosive, 46.75)
        self.assertAlmostEqual(dps.total, 150.7)
