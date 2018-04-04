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


from eos import FighterSquad
from eos import Fit
from eos import State
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from eos.const.eve import EffectId
from eos.const.eve import FighterAbilityId
from eos.eve_obj.type import AbilityData
from tests.integration.item.testcase import ItemMixinTestCase


class TestFighterSquadMissileSalvoDps(ItemMixinTestCase):

    def setUp(self):
        ItemMixinTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.fighter_ability_missiles_dmg_mult)
        self.mkattr(attr_id=AttrId.fighter_ability_missiles_dmg_em)
        self.mkattr(attr_id=AttrId.fighter_ability_missiles_dmg_therm)
        self.mkattr(attr_id=AttrId.fighter_ability_missiles_dmg_kin)
        self.mkattr(attr_id=AttrId.fighter_ability_missiles_dmg_expl)
        self.mkattr(attr_id=AttrId.fighter_squadron_max_size)
        self.cycle_attr = self.mkattr()
        self.effect = self.mkeffect(
            effect_id=EffectId.fighter_ability_missiles,
            category_id=EffectCategoryId.target,
            duration_attr_id=self.cycle_attr.id)
        self.abilities_data = {
            FighterAbilityId.heavy_rocket_salvo_em: AbilityData(0, 12)}

    def make_item(self, attrs):
        return FighterSquad(
            self.mktype(
                attrs=attrs,
                effects=[self.effect],
                default_effect=self.effect,
                abilities_data=self.abilities_data).id,
            state=State.active)

    def test_no_reload(self):
        fit = Fit()
        item = self.make_item({
            AttrId.fighter_ability_missiles_dmg_mult: 2.5,
            AttrId.fighter_ability_missiles_dmg_em: 52,
            AttrId.fighter_ability_missiles_dmg_therm: 63,
            AttrId.fighter_ability_missiles_dmg_kin: 74,
            AttrId.fighter_ability_missiles_dmg_expl: 85,
            AttrId.fighter_squadron_max_size: 9,
            self.cycle_attr.id: 4000})
        fit.fighters.add(item)
        # Verification
        dps = item.get_dps(reload=False)
        self.assertAlmostEqual(dps.em, 292.5)
        self.assertAlmostEqual(dps.thermal, 354.375)
        self.assertAlmostEqual(dps.kinetic, 416.25)
        self.assertAlmostEqual(dps.explosive, 478.125)
        self.assertAlmostEqual(dps.total, 1541.25)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_reload(self):
        fit = Fit()
        item = self.make_item({
            AttrId.fighter_ability_missiles_dmg_mult: 2.5,
            AttrId.fighter_ability_missiles_dmg_em: 52,
            AttrId.fighter_ability_missiles_dmg_therm: 63,
            AttrId.fighter_ability_missiles_dmg_kin: 74,
            AttrId.fighter_ability_missiles_dmg_expl: 85,
            AttrId.fighter_squadron_max_size: 9,
            self.cycle_attr.id: 4000})
        fit.fighters.add(item)
        # Verification
        dps = item.get_dps(reload=True)
        self.assertAlmostEqual(dps.em, 292.5)
        self.assertAlmostEqual(dps.thermal, 354.375)
        self.assertAlmostEqual(dps.kinetic, 416.25)
        self.assertAlmostEqual(dps.explosive, 478.125)
        self.assertAlmostEqual(dps.total, 1541.25)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)
