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


import math

from eos import FighterSquad
from eos import Fit
from eos import State
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from eos.const.eve import EffectId
from eos.const.eve import FighterAbilityId
from eos.eve_object.type import AbilityData
from tests.integration.item.testcase import ItemMixinTestCase


class TestFighterSquadKamikazeSuppression(ItemMixinTestCase):

    def setUp(self):
        ItemMixinTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.fighter_ability_attack_missile_dmg_mult)
        self.mkattr(attr_id=AttrId.fighter_ability_attack_missile_dmg_em)
        self.mkattr(attr_id=AttrId.fighter_ability_attack_missile_dmg_therm)
        self.mkattr(attr_id=AttrId.fighter_ability_attack_missile_dmg_kin)
        self.mkattr(attr_id=AttrId.fighter_ability_attack_missile_dmg_expl)
        self.mkattr(attr_id=AttrId.fighter_ability_kamikaze_dmg_em)
        self.mkattr(attr_id=AttrId.fighter_ability_kamikaze_dmg_therm)
        self.mkattr(attr_id=AttrId.fighter_ability_kamikaze_dmg_kin)
        self.mkattr(attr_id=AttrId.fighter_ability_kamikaze_dmg_expl)
        self.mkattr(attr_id=AttrId.fighter_squadron_max_size)
        self.cycle_attr = self.mkattr()
        self.effect_attack = self.mkeffect(
            effect_id=EffectId.fighter_ability_attack_m,
            category_id=EffectCategoryId.target)
        self.effect_kamikaze = self.mkeffect(
            effect_id=EffectId.fighter_ability_kamikaze,
            category_id=EffectCategoryId.target,
            duration_attr_id=self.cycle_attr.id)
        self.abilities_data = {
            FighterAbilityId.pulse_cannon: AbilityData(0, math.inf),
            FighterAbilityId.kamikaze: AbilityData(0, math.inf)}

    def make_item(self, attrs):
        return FighterSquad(
            self.mktype(
                attrs=attrs,
                effects=(self.effect_attack, self.effect_kamikaze),
                default_effect=self.effect_attack,
                abilities_data=self.abilities_data).id,
            state=State.active)

    def test_suppressing(self):
        fit = Fit()
        item = self.make_item({
            AttrId.fighter_ability_attack_missile_dmg_mult: 2.5,
            AttrId.fighter_ability_attack_missile_dmg_em: 52,
            AttrId.fighter_ability_attack_missile_dmg_therm: 63,
            AttrId.fighter_ability_attack_missile_dmg_kin: 74,
            AttrId.fighter_ability_attack_missile_dmg_expl: 85,
            AttrId.fighter_ability_kamikaze_dmg_em: 50000,
            AttrId.fighter_ability_kamikaze_dmg_therm: 50000,
            AttrId.fighter_ability_kamikaze_dmg_kin: 50000,
            AttrId.fighter_ability_kamikaze_dmg_expl: 50000,
            AttrId.fighter_squadron_max_size: 6})
        fit.fighters.add(item)
        item.set_ability_status(FighterAbilityId.kamikaze, True)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 300000)
        self.assertAlmostEqual(volley.thermal, 300000)
        self.assertAlmostEqual(volley.kinetic, 300000)
        self.assertAlmostEqual(volley.explosive, 300000)
        self.assertAlmostEqual(volley.total, 1200000)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_not_suppressing(self):
        fit = Fit()
        item = self.make_item({
            AttrId.fighter_ability_attack_missile_dmg_mult: 2.5,
            AttrId.fighter_ability_attack_missile_dmg_em: 52,
            AttrId.fighter_ability_attack_missile_dmg_therm: 63,
            AttrId.fighter_ability_attack_missile_dmg_kin: 74,
            AttrId.fighter_ability_attack_missile_dmg_expl: 85,
            AttrId.fighter_ability_kamikaze_dmg_em: 50000,
            AttrId.fighter_ability_kamikaze_dmg_therm: 50000,
            AttrId.fighter_ability_kamikaze_dmg_kin: 50000,
            AttrId.fighter_ability_kamikaze_dmg_expl: 50000,
            AttrId.fighter_squadron_max_size: 6})
        fit.fighters.add(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 780)
        self.assertAlmostEqual(volley.thermal, 945)
        self.assertAlmostEqual(volley.kinetic, 1110)
        self.assertAlmostEqual(volley.explosive, 1275)
        self.assertAlmostEqual(volley.total, 4110)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)
