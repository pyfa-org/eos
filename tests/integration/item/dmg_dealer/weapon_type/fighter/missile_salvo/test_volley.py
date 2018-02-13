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

    def make_fighter(self, attrs):
        return FighterSquad(
            self.mktype(
                attrs=attrs,
                effects=[self.effect],
                default_effect=self.effect,
                abilities_data=self.abilities_data).id,
            state=State.active)

    def test_generic(self):
        fit = Fit()
        item = self.make_fighter({
            AttrId.fighter_ability_missiles_dmg_mult: 2.5,
            AttrId.fighter_ability_missiles_dmg_em: 52,
            AttrId.fighter_ability_missiles_dmg_therm: 63,
            AttrId.fighter_ability_missiles_dmg_kin: 74,
            AttrId.fighter_ability_missiles_dmg_expl: 85,
            AttrId.fighter_squadron_max_size: 9})
        fit.fighters.add(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 1170)
        self.assertAlmostEqual(volley.thermal, 1417.5)
        self.assertAlmostEqual(volley.kinetic, 1665)
        self.assertAlmostEqual(volley.explosive, 1912.5)
        self.assertAlmostEqual(volley.total, 6165)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_attr_em(self):
        fit = Fit()
        item = self.make_fighter({
            AttrId.fighter_ability_missiles_dmg_mult: 2.5,
            AttrId.fighter_ability_missiles_dmg_therm: 63,
            AttrId.fighter_ability_missiles_dmg_kin: 74,
            AttrId.fighter_ability_missiles_dmg_expl: 85,
            AttrId.fighter_squadron_max_size: 9})
        fit.fighters.add(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 0)
        self.assertAlmostEqual(volley.thermal, 1417.5)
        self.assertAlmostEqual(volley.kinetic, 1665)
        self.assertAlmostEqual(volley.explosive, 1912.5)
        self.assertAlmostEqual(volley.total, 4995)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_attr_therm(self):
        fit = Fit()
        item = self.make_fighter({
            AttrId.fighter_ability_missiles_dmg_mult: 2.5,
            AttrId.fighter_ability_missiles_dmg_em: 52,
            AttrId.fighter_ability_missiles_dmg_kin: 74,
            AttrId.fighter_ability_missiles_dmg_expl: 85,
            AttrId.fighter_squadron_max_size: 9})
        fit.fighters.add(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 1170)
        self.assertAlmostEqual(volley.thermal, 0)
        self.assertAlmostEqual(volley.kinetic, 1665)
        self.assertAlmostEqual(volley.explosive, 1912.5)
        self.assertAlmostEqual(volley.total, 4747.5)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_attr_kin(self):
        fit = Fit()
        item = self.make_fighter({
            AttrId.fighter_ability_missiles_dmg_mult: 2.5,
            AttrId.fighter_ability_missiles_dmg_em: 52,
            AttrId.fighter_ability_missiles_dmg_therm: 63,
            AttrId.fighter_ability_missiles_dmg_expl: 85,
            AttrId.fighter_squadron_max_size: 9})
        fit.fighters.add(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 1170)
        self.assertAlmostEqual(volley.thermal, 1417.5)
        self.assertAlmostEqual(volley.kinetic, 0)
        self.assertAlmostEqual(volley.explosive, 1912.5)
        self.assertAlmostEqual(volley.total, 4500)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_attr_expl(self):
        fit = Fit()
        item = self.make_fighter({
            AttrId.fighter_ability_missiles_dmg_mult: 2.5,
            AttrId.fighter_ability_missiles_dmg_em: 52,
            AttrId.fighter_ability_missiles_dmg_therm: 63,
            AttrId.fighter_ability_missiles_dmg_kin: 74,
            AttrId.fighter_squadron_max_size: 9})
        fit.fighters.add(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 1170)
        self.assertAlmostEqual(volley.thermal, 1417.5)
        self.assertAlmostEqual(volley.kinetic, 1665)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 4252.5)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_mult(self):
        fit = Fit()
        item = self.make_fighter({
            AttrId.fighter_ability_missiles_dmg_em: 52,
            AttrId.fighter_ability_missiles_dmg_therm: 63,
            AttrId.fighter_ability_missiles_dmg_kin: 74,
            AttrId.fighter_ability_missiles_dmg_expl: 85,
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

    def test_no_squad_size(self):
        fit = Fit()
        item = Drone(
            self.mktype(
                attrs={
                    AttrId.fighter_ability_missiles_dmg_mult: 2.5,
                    AttrId.fighter_ability_missiles_dmg_em: 52,
                    AttrId.fighter_ability_missiles_dmg_therm: 63,
                    AttrId.fighter_ability_missiles_dmg_kin: 74,
                    AttrId.fighter_ability_missiles_dmg_expl: 85},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        fit.drones.add(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 130)
        self.assertAlmostEqual(volley.thermal, 157.5)
        self.assertAlmostEqual(volley.kinetic, 185)
        self.assertAlmostEqual(volley.explosive, 212.5)
        self.assertAlmostEqual(volley.total, 685)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)
