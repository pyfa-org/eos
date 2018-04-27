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

from eos import Drone
from eos import FighterSquad
from eos import Fit
from eos import State
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from eos.const.eve import EffectId
from eos.const.eve import FighterAbilityId
from eos.eve_obj.type import AbilityData
from tests.integration.item.testcase import ItemMixinTestCase


class TestFighterSquadKamikazeDps(ItemMixinTestCase):

    def setUp(self):
        ItemMixinTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.fighter_ability_kamikaze_dmg_em)
        self.mkattr(attr_id=AttrId.fighter_ability_kamikaze_dmg_therm)
        self.mkattr(attr_id=AttrId.fighter_ability_kamikaze_dmg_kin)
        self.mkattr(attr_id=AttrId.fighter_ability_kamikaze_dmg_expl)
        self.mkattr(attr_id=AttrId.fighter_squadron_max_size)
        self.cycle_attr = self.mkattr()
        self.effect = self.mkeffect(
            effect_id=EffectId.fighter_ability_kamikaze,
            category_id=EffectCategoryId.target,
            duration_attr_id=self.cycle_attr.id)
        self.abilities_data = {
            FighterAbilityId.kamikaze: AbilityData(0, math.inf)}

    def make_item(self, attrs, item_class=FighterSquad):
        return item_class(
            self.mktype(
                attrs=attrs,
                effects=[self.effect],
                default_effect=self.effect,
                abilities_data=self.abilities_data).id,
            state=State.active)

    def test_generic(self):
        fit = Fit()
        item = self.make_item({
            AttrId.fighter_ability_kamikaze_dmg_em: 50000,
            AttrId.fighter_ability_kamikaze_dmg_therm: 50000,
            AttrId.fighter_ability_kamikaze_dmg_kin: 50000,
            AttrId.fighter_ability_kamikaze_dmg_expl: 50000,
            AttrId.fighter_squadron_max_size: 6})
        fit.fighters.add(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 300000)
        self.assertAlmostEqual(volley.thermal, 300000)
        self.assertAlmostEqual(volley.kinetic, 300000)
        self.assertAlmostEqual(volley.explosive, 300000)
        self.assertAlmostEqual(volley.total, 1200000)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_attr_em_absent(self):
        fit = Fit()
        item = self.make_item({
            AttrId.fighter_ability_kamikaze_dmg_therm: 50000,
            AttrId.fighter_ability_kamikaze_dmg_kin: 50000,
            AttrId.fighter_ability_kamikaze_dmg_expl: 50000,
            AttrId.fighter_squadron_max_size: 6})
        fit.fighters.add(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 0)
        self.assertAlmostEqual(volley.thermal, 300000)
        self.assertAlmostEqual(volley.kinetic, 300000)
        self.assertAlmostEqual(volley.explosive, 300000)
        self.assertAlmostEqual(volley.total, 900000)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_attr_therm_absent(self):
        fit = Fit()
        item = self.make_item({
            AttrId.fighter_ability_kamikaze_dmg_em: 50000,
            AttrId.fighter_ability_kamikaze_dmg_kin: 50000,
            AttrId.fighter_ability_kamikaze_dmg_expl: 50000,
            AttrId.fighter_squadron_max_size: 6})
        fit.fighters.add(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 300000)
        self.assertAlmostEqual(volley.thermal, 0)
        self.assertAlmostEqual(volley.kinetic, 300000)
        self.assertAlmostEqual(volley.explosive, 300000)
        self.assertAlmostEqual(volley.total, 900000)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_attr_kin_absent(self):
        fit = Fit()
        item = self.make_item({
            AttrId.fighter_ability_kamikaze_dmg_em: 50000,
            AttrId.fighter_ability_kamikaze_dmg_therm: 50000,
            AttrId.fighter_ability_kamikaze_dmg_expl: 50000,
            AttrId.fighter_squadron_max_size: 6})
        fit.fighters.add(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 300000)
        self.assertAlmostEqual(volley.thermal, 300000)
        self.assertAlmostEqual(volley.kinetic, 0)
        self.assertAlmostEqual(volley.explosive, 300000)
        self.assertAlmostEqual(volley.total, 900000)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_attr_expl_absent(self):
        fit = Fit()
        item = self.make_item({
            AttrId.fighter_ability_kamikaze_dmg_em: 50000,
            AttrId.fighter_ability_kamikaze_dmg_therm: 50000,
            AttrId.fighter_ability_kamikaze_dmg_kin: 50000,
            AttrId.fighter_squadron_max_size: 6})
        fit.fighters.add(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 300000)
        self.assertAlmostEqual(volley.thermal, 300000)
        self.assertAlmostEqual(volley.kinetic, 300000)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 900000)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_item_squad_size_absent(self):
        fit = Fit()
        item = self.make_item(
            attrs={
                AttrId.fighter_ability_kamikaze_dmg_em: 50000,
                AttrId.fighter_ability_kamikaze_dmg_therm: 50000,
                AttrId.fighter_ability_kamikaze_dmg_kin: 50000,
                AttrId.fighter_ability_kamikaze_dmg_expl: 50000,
                AttrId.fighter_squadron_max_size: 6},
            item_class=Drone)
        fit.drones.add(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 50000)
        self.assertAlmostEqual(volley.thermal, 50000)
        self.assertAlmostEqual(volley.kinetic, 50000)
        self.assertAlmostEqual(volley.explosive, 50000)
        self.assertAlmostEqual(volley.total, 200000)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)
