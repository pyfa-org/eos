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


from eos import FighterSquad
from eos import Fit
from eos import State
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from eos.const.eve import EffectId
from eos.const.eve import FighterAbilityId
from eos.eve_object.type import AbilityData
from tests.integration.item.testcase import ItemMixinTestCase


class TestFighterSquadLaunchBombDps(ItemMixinTestCase):

    def setUp(self):
        ItemMixinTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.em_dmg)
        self.mkattr(attr_id=AttrId.therm_dmg)
        self.mkattr(attr_id=AttrId.kin_dmg)
        self.mkattr(attr_id=AttrId.expl_dmg)
        self.mkattr(attr_id=AttrId.fighter_squadron_max_size)
        self.cycle_attr = self.mkattr()
        self.effect_item = self.mkeffect(
            effect_id=EffectId.fighter_ability_launch_bomb,
            category_id=EffectCategoryId.active,
            duration_attr_id=self.cycle_attr.id)
        self.effect_charge = self.mkeffect(
            effect_id=EffectId.bomb_launching,
            category_id=EffectCategoryId.active)
        self.abilities_data = {FighterAbilityId.launch_bomb: AbilityData(0, 3)}

    def make_item(self, attrs):
        return FighterSquad(
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

    def test_no_reload(self):
        fit = Fit()
        bomb_type = self.make_charge_type({
            AttrId.em_dmg: 52,
            AttrId.therm_dmg: 63,
            AttrId.kin_dmg: 74,
            AttrId.expl_dmg: 85})
        item = self.make_item({
            AttrId.fighter_ability_launch_bomb_type: bomb_type.id,
            AttrId.fighter_squadron_max_size: 9,
            self.cycle_attr.id: 60000})
        fit.fighters.add(item)
        # Verification
        dps = item.get_dps(reload=False)
        self.assertAlmostEqual(dps.em, 7.8)
        self.assertAlmostEqual(dps.thermal, 9.45)
        self.assertAlmostEqual(dps.kinetic, 11.1)
        self.assertAlmostEqual(dps.explosive, 12.75)
        self.assertAlmostEqual(dps.total, 41.1)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_reload(self):
        fit = Fit()
        bomb_type = self.make_charge_type({
            AttrId.em_dmg: 52,
            AttrId.therm_dmg: 63,
            AttrId.kin_dmg: 74,
            AttrId.expl_dmg: 85})
        item = self.make_item({
            AttrId.fighter_ability_launch_bomb_type: bomb_type.id,
            AttrId.fighter_squadron_max_size: 9,
            self.cycle_attr.id: 60000})
        fit.fighters.add(item)
        # Verification
        dps = item.get_dps(reload=True)
        self.assertAlmostEqual(dps.em, 7.8)
        self.assertAlmostEqual(dps.thermal, 9.45)
        self.assertAlmostEqual(dps.kinetic, 11.1)
        self.assertAlmostEqual(dps.explosive, 12.75)
        self.assertAlmostEqual(dps.total, 41.1)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)
