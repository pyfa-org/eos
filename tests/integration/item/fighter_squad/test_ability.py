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

from eos import FighterSquad
from eos import Fit
from eos import NoSuchAbilityError
from eos import State
from eos.const.eos import ModAffecteeFilter
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eve import EffectCategoryId
from eos.const.eve import EffectId
from eos.const.eve import FighterAbilityId
from eos.eve_obj.type import AbilityData
from tests.integration.item.testcase import ItemMixinTestCase


class TestItemFighterSquadAbility(ItemMixinTestCase):

    def test_status_item_active(self):
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
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_status_item_inactive(self):
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
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_status_item_not_loaded(self):
        # Setup
        fit = Fit()
        item = FighterSquad(self.allocate_type_id(), state=State.active)
        fit.fighters.add(item)
        # Verification
        self.assertEqual(len(item.abilities), 0)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_ability_enabling_default_effect(self):
        # Setup
        src_attr = self.mkattr()
        tgt_attr = self.mkattr()
        modifier = self.mkmod(
            affectee_filter=ModAffecteeFilter.item,
            affectee_domain=ModDomain.self,
            affectee_attr_id=tgt_attr.id,
            operator=ModOperator.post_percent,
            affector_attr_id=src_attr.id)
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
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_ability_enabling_nondefault_effect(self):
        # Setup
        src_attr = self.mkattr()
        tgt_attr = self.mkattr()
        modifier = self.mkmod(
            affectee_filter=ModAffecteeFilter.item,
            affectee_domain=ModDomain.self,
            affectee_attr_id=tgt_attr.id,
            operator=ModOperator.post_percent,
            affector_attr_id=src_attr.id)
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
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_ability_enabling_no_ability(self):
        # Setup
        src_attr = self.mkattr()
        tgt_attr = self.mkattr()
        modifier = self.mkmod(
            affectee_filter=ModAffecteeFilter.item,
            affectee_domain=ModDomain.self,
            affectee_attr_id=tgt_attr.id,
            operator=ModOperator.post_percent,
            affector_attr_id=src_attr.id)
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
        # Verification
        with self.assertRaises(NoSuchAbilityError):
            item.set_ability_status(FighterAbilityId.beam_cannon, True)
        self.assertIs(item.abilities[FighterAbilityId.pulse_cannon], False)
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 10)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_ability_enabling_item_not_loaded(self):
        # Setup
        fit = Fit()
        item = FighterSquad(self.allocate_type_id(), state=State.active)
        fit.fighters.add(item)
        # Verification
        with self.assertRaises(NoSuchAbilityError):
            item.set_ability_status(FighterAbilityId.beam_cannon, True)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_ability_disabling_default_effect(self):
        # Setup
        src_attr = self.mkattr()
        tgt_attr = self.mkattr()
        modifier = self.mkmod(
            affectee_filter=ModAffecteeFilter.item,
            affectee_domain=ModDomain.self,
            affectee_attr_id=tgt_attr.id,
            operator=ModOperator.post_percent,
            affector_attr_id=src_attr.id)
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
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_ability_disabling_nondefault_effect(self):
        # Setup
        src_attr = self.mkattr()
        tgt_attr = self.mkattr()
        modifier = self.mkmod(
            affectee_filter=ModAffecteeFilter.item,
            affectee_domain=ModDomain.self,
            affectee_attr_id=tgt_attr.id,
            operator=ModOperator.post_percent,
            affector_attr_id=src_attr.id)
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
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_ability_disabling_no_ability(self):
        # Setup
        src_attr = self.mkattr()
        tgt_attr = self.mkattr()
        modifier = self.mkmod(
            affectee_filter=ModAffecteeFilter.item,
            affectee_domain=ModDomain.self,
            affectee_attr_id=tgt_attr.id,
            operator=ModOperator.post_percent,
            affector_attr_id=src_attr.id)
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
        # Verification
        with self.assertRaises(NoSuchAbilityError):
            item.set_ability_status(FighterAbilityId.beam_cannon, False)
        self.assertIs(item.abilities[FighterAbilityId.pulse_cannon], True)
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 15)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_ability_disabling_item_not_loaded(self):
        # Setup
        fit = Fit()
        item = FighterSquad(self.allocate_type_id(), state=State.active)
        fit.fighters.add(item)
        # Verification
        with self.assertRaises(NoSuchAbilityError):
            item.set_ability_status(FighterAbilityId.beam_cannon, False)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)
