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


import logging

from eos.const.eve import EffectId
from eos.const.eve import FighterAbilityId
from tests.eve_obj_builder.testcase import EveObjBuilderTestCase


class TestFighterAbilities(EveObjBuilderTestCase):
    """Check that only known abilities in valud configurations pass."""

    logger_name = 'eos.data.eve_obj_builder.validator_preconv'

    def test_unknown_ability(self):
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 6})
        self.dh.data['evegroups'].append({'categoryID': 16, 'groupID': 6})
        self.dh.data['dgmtypeeffects'].append({
            'typeID': 1, 'effectID': EffectId.fighter_ability_attack_m,
            'isDefault': True})
        self.dh.data['dgmeffects'].append(
            {'effectID': EffectId.fighter_ability_attack_m})
        self.dh.data['typefighterabils'].append({'typeID': 1, 'abilityID': 555})
        self.run_builder()
        self.assertEqual(len(self.types), 1)
        self.assertIn(1, self.types)
        self.assertEqual(len(self.types[1].effects_data), 0)
        self.assertEqual(len(self.types[1].ability_ids), 0)
        log = self.get_log(name=self.logger_name)
        self.assertEqual(len(log), 1)
        log_record = log[0]
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(
            log_record.msg,
            '1 rows contain invalid fighter ability attributes, removing them')

    def test_ability_effect_collision(self):
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 6})
        self.dh.data['evegroups'].append({'categoryID': 16, 'groupID': 6})
        self.dh.data['dgmtypeeffects'].append({
            'typeID': 1, 'effectID': EffectId.fighter_ability_attack_m,
            'isDefault': True})
        self.dh.data['dgmeffects'].append(
            {'effectID': EffectId.fighter_ability_attack_m})
        self.dh.data['typefighterabils'].append({
            'typeID': 1, 'abilityID': FighterAbilityId.micromissile_swarm_em,
            'chargeCount': 3})
        self.dh.data['typefighterabils'].append({
            'typeID': 1, 'abilityID': FighterAbilityId.micromissile_swarm_exp,
            'chargeCount': 22})
        self.run_builder()
        self.assertEqual(len(self.types), 1)
        self.assertIn(1, self.types)
        type_effects_data = self.types[1].effects_data
        self.assertEqual(len(type_effects_data), 1)
        self.assertIn(EffectId.fighter_ability_missiles, type_effects_data)
        type_effect_data = type_effects_data[EffectId.fighter_ability_missiles]
        self.assertEqual(type_effect_data.charge_quantity, 3)
        self.assertCountEqual(
            self.types[1].ability_ids,
            [FighterAbilityId.micromissile_swarm_em])
        log = self.get_log(name=self.logger_name)
        self.assertEqual(len(log), 1)
        log_record = log[0]
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(
            log_record.msg,
            '1 rows contain invalid fighter ability attributes, removing them')

    def test_cleaned(self):
        self.dh.data['evetypes'].append({'typeID': 1})
        self.dh.data['dgmtypeeffects'].append({
            'typeID': 1, 'effectID': EffectId.fighter_ability_attack_m,
            'isDefault': True})
        self.dh.data['dgmeffects'].append(
            {'effectID': EffectId.fighter_ability_attack_m})
        self.dh.data['typefighterabils'].append({'typeID': 1, 'abilityID': 555})
        self.run_builder()
        self.assertEqual(len(self.types), 0)
        self.assertEqual(len(self.effects), 0)
        self.assertEqual(len(self.get_log(name=self.logger_name)), 0)
