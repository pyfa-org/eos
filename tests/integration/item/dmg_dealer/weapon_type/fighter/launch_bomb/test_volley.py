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


from eos import Drone
from eos import FighterSquad
from eos import Fit
from eos import State
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from eos.const.eve import EffectId
from eos.const.eve import FighterAbilityId
from eos.eve_object.type import AbilityData
from tests.integration.item.testcase import ItemMixinTestCase


class TestFighterSquadLaunchBombVolley(ItemMixinTestCase):

    def setUp(self):
        ItemMixinTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.em_dmg)
        self.mkattr(attr_id=AttrId.therm_dmg)
        self.mkattr(attr_id=AttrId.kin_dmg)
        self.mkattr(attr_id=AttrId.expl_dmg)
        self.mkattr(attr_id=AttrId.fighter_squadron_max_size)
        self.effect_item = self.mkeffect(
            effect_id=EffectId.fighter_ability_launch_bomb,
            category_id=EffectCategoryId.active)
        self.effect_charge = self.mkeffect(
            effect_id=EffectId.bomb_launching,
            category_id=EffectCategoryId.active)
        self.abilities_data = {FighterAbilityId.launch_bomb: AbilityData(0, 3)}

    def make_item(self, attrs, item_class=FighterSquad):
        return item_class(
            self.mktype(
                attrs=attrs,
                effects=[self.effect_item],
                default_effect=self.effect_item,
                abilities_data=self.abilities_data).id,
            state=State.active)

    def make_charge_type(self, attrs):
        return self.mktype(
            attrs=attrs,
            effects=[self.effect_charge],
            default_effect=self.effect_charge)

    def test_generic(self):
        fit = Fit()
        bomb_type = self.make_charge_type({
            AttrId.em_dmg: 52,
            AttrId.therm_dmg: 63,
            AttrId.kin_dmg: 74,
            AttrId.expl_dmg: 85})
        item = self.make_item({
            AttrId.fighter_ability_launch_bomb_type: bomb_type.id,
            AttrId.fighter_squadron_max_size: 9})
        fit.fighters.add(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 468)
        self.assertAlmostEqual(volley.thermal, 567)
        self.assertAlmostEqual(volley.kinetic, 666)
        self.assertAlmostEqual(volley.explosive, 765)
        self.assertAlmostEqual(volley.total, 2466)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_attr_em(self):
        fit = Fit()
        bomb_type = self.make_charge_type({
            AttrId.therm_dmg: 63,
            AttrId.kin_dmg: 74,
            AttrId.expl_dmg: 85})
        item = self.make_item({
            AttrId.fighter_ability_launch_bomb_type: bomb_type.id,
            AttrId.fighter_squadron_max_size: 9})
        fit.fighters.add(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 0)
        self.assertAlmostEqual(volley.thermal, 567)
        self.assertAlmostEqual(volley.kinetic, 666)
        self.assertAlmostEqual(volley.explosive, 765)
        self.assertAlmostEqual(volley.total, 1998)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_attr_therm(self):
        fit = Fit()
        bomb_type = self.make_charge_type({
            AttrId.em_dmg: 52,
            AttrId.kin_dmg: 74,
            AttrId.expl_dmg: 85})
        item = self.make_item({
            AttrId.fighter_ability_launch_bomb_type: bomb_type.id,
            AttrId.fighter_squadron_max_size: 9})
        fit.fighters.add(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 468)
        self.assertAlmostEqual(volley.thermal, 0)
        self.assertAlmostEqual(volley.kinetic, 666)
        self.assertAlmostEqual(volley.explosive, 765)
        self.assertAlmostEqual(volley.total, 1899)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_attr_kin(self):
        fit = Fit()
        bomb_type = self.make_charge_type({
            AttrId.em_dmg: 52,
            AttrId.therm_dmg: 63,
            AttrId.expl_dmg: 85})
        item = self.make_item({
            AttrId.fighter_ability_launch_bomb_type: bomb_type.id,
            AttrId.fighter_squadron_max_size: 9})
        fit.fighters.add(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 468)
        self.assertAlmostEqual(volley.thermal, 567)
        self.assertAlmostEqual(volley.kinetic, 0)
        self.assertAlmostEqual(volley.explosive, 765)
        self.assertAlmostEqual(volley.total, 1800)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_attr_expl(self):
        fit = Fit()
        bomb_type = self.make_charge_type({
            AttrId.em_dmg: 52,
            AttrId.therm_dmg: 63,
            AttrId.kin_dmg: 74})
        item = self.make_item({
            AttrId.fighter_ability_launch_bomb_type: bomb_type.id,
            AttrId.fighter_squadron_max_size: 9})
        fit.fighters.add(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 468)
        self.assertAlmostEqual(volley.thermal, 567)
        self.assertAlmostEqual(volley.kinetic, 666)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 1701)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_squad_size(self):
        fit = Fit()
        bomb_type = self.make_charge_type({
            AttrId.em_dmg: 52,
            AttrId.therm_dmg: 63,
            AttrId.kin_dmg: 74,
            AttrId.expl_dmg: 85})
        item = self.make_item(
            attrs={
                AttrId.fighter_ability_launch_bomb_type: bomb_type.id,
                AttrId.fighter_squadron_max_size: 9},
            item_class=Drone)
        fit.drones.add(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 52)
        self.assertAlmostEqual(volley.thermal, 63)
        self.assertAlmostEqual(volley.kinetic, 74)
        self.assertAlmostEqual(volley.explosive, 85)
        self.assertAlmostEqual(volley.total, 274)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_charges(self):
        self.abilities_data = {FighterAbilityId.launch_bomb: AbilityData(0, 0)}
        fit = Fit()
        bomb_type = self.make_charge_type({
            AttrId.em_dmg: 52,
            AttrId.therm_dmg: 63,
            AttrId.kin_dmg: 74,
            AttrId.expl_dmg: 85})
        item = self.make_item({
            AttrId.fighter_ability_launch_bomb_type: bomb_type.id,
            AttrId.fighter_squadron_max_size: 9})
        fit.fighters.add(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 0)
        self.assertAlmostEqual(volley.thermal, 0)
        self.assertAlmostEqual(volley.kinetic, 0)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_charge_type_attr(self):
        fit = Fit()
        item = self.make_item({AttrId.fighter_squadron_max_size: 9})
        fit.fighters.add(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 0)
        self.assertAlmostEqual(volley.thermal, 0)
        self.assertAlmostEqual(volley.kinetic, 0)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_charge_type(self):
        fit = Fit()
        empty_type_id = self.allocate_type_id()
        item = self.make_item({
            AttrId.fighter_ability_launch_bomb_type: empty_type_id,
            AttrId.fighter_squadron_max_size: 9})
        fit.fighters.add(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 0)
        self.assertAlmostEqual(volley.thermal, 0)
        self.assertAlmostEqual(volley.kinetic, 0)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)
