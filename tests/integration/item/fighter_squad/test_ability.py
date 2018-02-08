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
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import FighterAbilityId
from eos.const.eve import EffectCategoryId
from eos.const.eve import EffectId
from eos.eve_object.type import AbilityData
from tests.integration.item.testcase import ItemMixinTestCase


class TestItemFighterSquadAbility(ItemMixinTestCase):

    def test_status_active(self):
        # Setup
        effect1 = self.mkeffect(
            effect_id=EffectId.fighter_ability_attack_m,
            category_id=EffectCategoryId.active)
        effect2 = self.mkeffect(
            effect_id=EffectId.fighter_ability_microwarpdrive,
            category_id=EffectCategoryId.active)
        effect3 = self.mkeffect(
            effect_id=EffectId.fighter_ability_missiles,
            category_id=EffectCategoryId.active)
        fighter_type = self.mktype(
            effects=(effect1, effect2, effect3),
            default_effect=effect1,
            abilities_data={
                FighterAbilityId.pulse_cannon: AbilityData(0, math.inf),
                FighterAbilityId.microwarpdrive: AbilityData(60, math.inf),
                FighterAbilityId.heavy_rocket_salvo_em: AbilityData(0, 12)})
        fit = Fit()
        item = FighterSquad(fighter_type.id, state=State.active)
        fit.fighters.add(item)
        # Verification
        abilities = item.abilities
        self.assertEqual(len(abilities), 3)
        self.assertIs(abilities[FighterAbilityId.pulse_cannon], True)
        self.assertIs(abilities[FighterAbilityId.microwarpdrive], False)
        self.assertIs(abilities[FighterAbilityId.heavy_rocket_salvo_em], False)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_status_inactive(self):
        # Even when item is not set to active, ability statuses should be shown
        # like item is active
        # Setup
        effect1 = self.mkeffect(
            effect_id=EffectId.fighter_ability_attack_m,
            category_id=EffectCategoryId.active)
        effect2 = self.mkeffect(
            effect_id=EffectId.fighter_ability_microwarpdrive,
            category_id=EffectCategoryId.active)
        effect3 = self.mkeffect(
            effect_id=EffectId.fighter_ability_missiles,
            category_id=EffectCategoryId.active)
        fighter_type = self.mktype(
            effects=(effect1, effect2, effect3),
            default_effect=effect1,
            abilities_data={
                FighterAbilityId.pulse_cannon: AbilityData(0, math.inf),
                FighterAbilityId.microwarpdrive: AbilityData(60, math.inf),
                FighterAbilityId.heavy_rocket_salvo_em: AbilityData(0, 12)})
        fit = Fit()
        item = FighterSquad(fighter_type.id, state=State.online)
        fit.fighters.add(item)
        # Verification
        abilities = item.abilities
        self.assertEqual(len(abilities), 3)
        self.assertIs(abilities[FighterAbilityId.pulse_cannon], True)
        self.assertIs(abilities[FighterAbilityId.microwarpdrive], False)
        self.assertIs(abilities[FighterAbilityId.heavy_rocket_salvo_em], False)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_status_no_source(self):
        # Setup
        effect1 = self.mkeffect(
            effect_id=EffectId.fighter_ability_attack_m,
            category_id=EffectCategoryId.active)
        effect2 = self.mkeffect(
            effect_id=EffectId.fighter_ability_microwarpdrive,
            category_id=EffectCategoryId.active)
        effect3 = self.mkeffect(
            effect_id=EffectId.fighter_ability_missiles,
            category_id=EffectCategoryId.active)
        fighter_type = self.mktype(
            effects=(effect1, effect2, effect3),
            default_effect=effect1,
            abilities_data={
                FighterAbilityId.pulse_cannon: AbilityData(0, math.inf),
                FighterAbilityId.microwarpdrive: AbilityData(60, math.inf),
                FighterAbilityId.heavy_rocket_salvo_em: AbilityData(0, 12)})
        fit = Fit()
        item = FighterSquad(fighter_type.id, state=State.active)
        fit.fighters.add(item)
        fit.source = None
        # Verification
        abilities = item.abilities
        self.assertEqual(len(abilities), 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_ability_enabling_default_effect(self):
        # Setup
        src_attr = self.mkattr()
        tgt_attr = self.mkattr()
        modifier = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=tgt_attr.id,
            operator=ModOperator.post_percent,
            src_attr_id=src_attr.id)
        effect = self.mkeffect(
            effect_id=EffectId.fighter_ability_attack_m,
            category_id=EffectCategoryId.active,
            modifiers=[modifier])
        fighter_type = self.mktype(
            attrs={src_attr.id: 50, tgt_attr.id: 10},
            effects=[effect],
            default_effect=effect,
            abilities_data={
                FighterAbilityId.pulse_cannon: AbilityData(0, math.inf)})
        fit = Fit()
        item = FighterSquad(fighter_type.id, state=State.active)
        fit.fighters.add(item)
        item.set_ability_status(FighterAbilityId.pulse_cannon, False)
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 10)
        # Action
        item.set_ability_status(FighterAbilityId.pulse_cannon, True)
        # Verification
        self.assertIs(item.abilities[FighterAbilityId.pulse_cannon], True)
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 15)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_ability_enabling_nondefault_effect(self):
        # Setup
        src_attr = self.mkattr()
        tgt_attr = self.mkattr()
        modifier = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=tgt_attr.id,
            operator=ModOperator.post_percent,
            src_attr_id=src_attr.id)
        effect = self.mkeffect(
            effect_id=EffectId.fighter_ability_attack_m,
            category_id=EffectCategoryId.active,
            modifiers=[modifier])
        fighter_type = self.mktype(
            attrs={src_attr.id: 50, tgt_attr.id: 10},
            effects=[effect],
            abilities_data={
                FighterAbilityId.pulse_cannon: AbilityData(0, math.inf)})
        fit = Fit()
        item = FighterSquad(fighter_type.id, state=State.active)
        fit.fighters.add(item)
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 10)
        # Action
        item.set_ability_status(FighterAbilityId.pulse_cannon, True)
        # Verification
        self.assertIs(item.abilities[FighterAbilityId.pulse_cannon], True)
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 15)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_ability_disabling_default_effect(self):
        # Setup
        src_attr = self.mkattr()
        tgt_attr = self.mkattr()
        modifier = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=tgt_attr.id,
            operator=ModOperator.post_percent,
            src_attr_id=src_attr.id)
        effect = self.mkeffect(
            effect_id=EffectId.fighter_ability_attack_m,
            category_id=EffectCategoryId.active,
            modifiers=[modifier])
        fighter_type = self.mktype(
            attrs={src_attr.id: 50, tgt_attr.id: 10},
            effects=[effect],
            default_effect=effect,
            abilities_data={
                FighterAbilityId.pulse_cannon: AbilityData(0, math.inf)})
        fit = Fit()
        item = FighterSquad(fighter_type.id, state=State.active)
        fit.fighters.add(item)
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 15)
        # Action
        item.set_ability_status(FighterAbilityId.pulse_cannon, False)
        # Verification
        self.assertIs(item.abilities[FighterAbilityId.pulse_cannon], False)
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 10)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_ability_disabling_nondefault_effect(self):
        # Setup
        src_attr = self.mkattr()
        tgt_attr = self.mkattr()
        modifier = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=tgt_attr.id,
            operator=ModOperator.post_percent,
            src_attr_id=src_attr.id)
        effect = self.mkeffect(
            effect_id=EffectId.fighter_ability_attack_m,
            category_id=EffectCategoryId.active,
            modifiers=[modifier])
        fighter_type = self.mktype(
            attrs={src_attr.id: 50, tgt_attr.id: 10},
            effects=[effect],
            abilities_data={
                FighterAbilityId.pulse_cannon: AbilityData(0, math.inf)})
        fit = Fit()
        item = FighterSquad(fighter_type.id, state=State.active)
        fit.fighters.add(item)
        item.set_ability_status(FighterAbilityId.pulse_cannon, True)
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 15)
        # Action
        item.set_ability_status(FighterAbilityId.pulse_cannon, False)
        # Verification
        self.assertIs(item.abilities[FighterAbilityId.pulse_cannon], False)
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 10)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    # def test_data_no_source(self):
    #     # Setup
    #     chance_attr1 = self.mkattr()
    #     chance_attr2 = self.mkattr()
    #     src_attr = self.mkattr()
    #     modifier = self.mkmod(
    #         tgt_filter=ModTgtFilter.item,
    #         tgt_domain=ModDomain.self,
    #         tgt_attr_id=chance_attr2.id,
    #         operator=ModOperator.post_percent,
    #         src_attr_id=src_attr.id)
    #     effect1 = self.mkeffect(
    #         category_id=EffectCategoryId.passive,
    #         fitting_usage_chance_attr_id=chance_attr1.id)
    #     effect2 = self.mkeffect(
    #         category_id=EffectCategoryId.passive,
    #         fitting_usage_chance_attr_id=chance_attr2.id)
    #     effect3 = self.mkeffect(
    #         category_id=EffectCategoryId.passive,
    #         modifiers=[modifier])
    #     fit = Fit(source=None)
    #     item = Booster(self.mktype(
    #         attrs={
    #             chance_attr1.id: 0.5,
    #             chance_attr2.id: 0.1,
    #             src_attr.id: -25},
    #         effects=(effect1, effect2, effect3)).id)
    #     fit.boosters.add(item)
    #     item.set_side_effect_status(effect2.id, True)
    #     # Verification
    #     side_effects = item.side_effects
    #     self.assertEqual(len(side_effects), 0)
    #     self.assertNotIn(effect1.id, side_effects)
    #     self.assertNotIn(effect2.id, side_effects)
    #     # Cleanup
    #     self.assert_fit_buffers_empty(fit)
    #     self.assertEqual(len(self.get_log()), 0)
    #
    # def test_enabling(self):
    #     # Setup
    #     chance_attr = self.mkattr()
    #     src_attr = self.mkattr()
    #     tgt_attr = self.mkattr()
    #     modifier = self.mkmod(
    #         tgt_filter=ModTgtFilter.item,
    #         tgt_domain=ModDomain.self,
    #         tgt_attr_id=tgt_attr.id,
    #         operator=ModOperator.post_mul,
    #         src_attr_id=src_attr.id)
    #     effect = self.mkeffect(
    #         category_id=EffectCategoryId.passive,
    #         fitting_usage_chance_attr_id=chance_attr.id,
    #         modifiers=[modifier])
    #     fit = Fit()
    #     item = Booster(self.mktype(
    #         attrs={
    #             chance_attr.id: 0.5,
    #             tgt_attr.id: 100,
    #             src_attr.id: 1.2},
    #         effects=[effect]).id)
    #     fit.boosters.add(item)
    #     self.assertAlmostEqual(item.attrs[tgt_attr.id], 100)
    #     # Action
    #     item.set_side_effect_status(effect.id, True)
    #     # Verification
    #     self.assertIs(item.side_effects[effect.id].status, True)
    #     self.assertAlmostEqual(item.attrs[tgt_attr.id], 120)
    #     # Cleanup
    #     self.assert_fit_buffers_empty(fit)
    #     self.assertEqual(len(self.get_log()), 0)
    #
    # def test_disabling(self):
    #     # Setup
    #     chance_attr = self.mkattr()
    #     src_attr = self.mkattr()
    #     tgt_attr = self.mkattr()
    #     modifier = self.mkmod(
    #         tgt_filter=ModTgtFilter.item,
    #         tgt_domain=ModDomain.self,
    #         tgt_attr_id=tgt_attr.id,
    #         operator=ModOperator.post_mul,
    #         src_attr_id=src_attr.id)
    #     effect = self.mkeffect(
    #         category_id=EffectCategoryId.passive,
    #         fitting_usage_chance_attr_id=chance_attr.id,
    #         modifiers=[modifier])
    #     fit = Fit()
    #     item = Booster(self.mktype(
    #         attrs={
    #             chance_attr.id: 0.5,
    #             tgt_attr.id: 100,
    #             src_attr.id: 1.2},
    #         effects=[effect]).id)
    #     fit.boosters.add(item)
    #     item.set_side_effect_status(effect.id, True)
    #     self.assertAlmostEqual(item.attrs[tgt_attr.id], 120)
    #     # Action
    #     item.set_side_effect_status(effect.id, False)
    #     # Verification
    #     self.assertIs(item.side_effects[effect.id].status, False)
    #     self.assertAlmostEqual(item.attrs[tgt_attr.id], 100)
    #     # Cleanup
    #     self.assert_fit_buffers_empty(fit)
    #     self.assertEqual(len(self.get_log()), 0)
