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


import math

from eos import Charge
from eos import FighterSquad
from eos import ModuleHigh
from eos import State
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from eos.const.eve import EffectId
from eos.const.eve import FighterAbilityId
from eos.eve_obj.type import AbilityData
from tests.integration.stats.testcase import StatsTestCase


class TestStatsDmgSuppression(StatsTestCase):
    """Suppressor effects should suppress only effects on its own items."""

    def setUp(self):
        StatsTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.em_dmg)
        self.mkattr(attr_id=AttrId.therm_dmg)
        self.mkattr(attr_id=AttrId.kin_dmg)
        self.mkattr(attr_id=AttrId.expl_dmg)
        self.mkattr(attr_id=AttrId.dmg_mult)
        self.mkattr(attr_id=AttrId.volume)
        self.mkattr(attr_id=AttrId.capacity)
        self.mkattr(attr_id=AttrId.reload_time)
        self.mkattr(attr_id=AttrId.charge_rate)
        self.mkattr(attr_id=AttrId.fighter_ability_kamikaze_dmg_em)
        self.mkattr(attr_id=AttrId.fighter_ability_kamikaze_dmg_therm)
        self.mkattr(attr_id=AttrId.fighter_ability_kamikaze_dmg_kin)
        self.mkattr(attr_id=AttrId.fighter_ability_kamikaze_dmg_expl)
        cycle_attr = self.mkattr()
        effect_dd = self.mkeffect(
            effect_id=EffectId.projectile_fired,
            category_id=EffectCategoryId.active,
            duration_attr_id=cycle_attr.id)
        effect_suppressor = self.mkeffect(
            effect_id=EffectId.fighter_ability_kamikaze,
            category_id=EffectCategoryId.target,
            duration_attr_id=cycle_attr.id)
        item_dd = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.dmg_mult: 2,
                    AttrId.capacity: 1,
                    AttrId.charge_rate: 1,
                    cycle_attr.id: 2500,
                    AttrId.reload_time: 2000},
                effects=[effect_dd],
                default_effect=effect_dd).id,
            state=State.active)
        item_dd.charge = Charge(self.mktype(attrs={
            AttrId.volume: 1.0,
            AttrId.em_dmg: 1.2,
            AttrId.therm_dmg: 2.4,
            AttrId.kin_dmg: 4.8,
            AttrId.expl_dmg: 9.6}).id)
        self.item_suppressor = FighterSquad(
            self.mktype(
                attrs={
                    AttrId.fighter_ability_kamikaze_dmg_em: 50000,
                    AttrId.fighter_ability_kamikaze_dmg_therm: 50000,
                    AttrId.fighter_ability_kamikaze_dmg_kin: 50000,
                    AttrId.fighter_ability_kamikaze_dmg_expl: 50000,
                    AttrId.fighter_squadron_max_size: 6,
                    cycle_attr.id: 10000},
                effects=[effect_suppressor],
                default_effect=effect_suppressor,
                abilities_data={
                    FighterAbilityId.kamikaze: AbilityData(0, math.inf)}).id,
            state=State.active)
        self.fit.modules.high.append(item_dd)
        self.fit.fighters.add(self.item_suppressor)

    def test_volley(self):
        # Action
        stats_volley = self.fit.stats.get_volley()
        # Verification
        self.assertAlmostEqual(stats_volley.em, 50002.4)
        self.assertAlmostEqual(stats_volley.thermal, 50004.8)
        self.assertAlmostEqual(stats_volley.kinetic, 50009.6)
        self.assertAlmostEqual(stats_volley.explosive, 50019.2)
        self.assertAlmostEqual(stats_volley.total, 200036.0)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_dps(self):
        # Action
        stats_volley = self.fit.stats.get_dps(reload=False)
        # Verification
        self.assertAlmostEqual(stats_volley.em, 0.96)
        self.assertAlmostEqual(stats_volley.thermal, 1.92)
        self.assertAlmostEqual(stats_volley.kinetic, 3.84)
        self.assertAlmostEqual(stats_volley.explosive, 7.68)
        self.assertAlmostEqual(stats_volley.total, 14.4)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)
