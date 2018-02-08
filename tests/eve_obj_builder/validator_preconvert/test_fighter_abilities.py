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
        self.dh.data['dgmtypeeffects'].append(
            {'typeID': 1, 'effectID': EffectId.fighter_ability_attack_m})
        self.dh.data['dgmeffects'].append(
            {'effectID': EffectId.fighter_ability_attack_m})
        self.dh.data['typefighterabils'].append({'typeID': 1, 'abilityID': 555})
        self.run_builder()
        self.assertEqual(len(self.types), 1)
        self.assertIn(1, self.types)
        self.assertEqual(len(self.types[1].abilities_data), 0)
        log = self.get_log(name=self.logger_name)
        self.assertEqual(len(log), 1)
        log_record = log[0]
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(
            log_record.msg,
            '1 rows contain unknown fighter abilities, removing them')

    def test_ability_effect_collision(self):
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 6})
        self.dh.data['evegroups'].append({'categoryID': 16, 'groupID': 6})
        self.dh.data['dgmtypeeffects'].append(
            {'typeID': 1, 'effectID': EffectId.fighter_ability_attack_m})
        self.dh.data['dgmeffects'].append(
            {'effectID': EffectId.fighter_ability_attack_m})
        self.dh.data['typefighterabils'].append({
            'typeID': 1, 'abilityID': FighterAbilityId.autocannon,
            'chargeCount': 3})
        self.dh.data['typefighterabils'].append({
            'typeID': 1, 'abilityID': FighterAbilityId.blaster_cannon,
            'chargeCount': 22})
        self.run_builder()
        self.assertEqual(len(self.types), 1)
        self.assertIn(1, self.types)
        type_abilities_data = self.types[1].abilities_data
        self.assertEqual(len(type_abilities_data), 1)
        type_ability_data = type_abilities_data[FighterAbilityId.autocannon]
        self.assertEqual(type_ability_data.charge_quantity, 3)
        log = self.get_log(name=self.logger_name)
        self.assertEqual(len(log), 1)
        log_record = log[0]
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(
            log_record.msg,
            '1 rows contain colliding fighter abilities, removing them')

    def test_ability_no_effect(self):
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 6})
        self.dh.data['evegroups'].append({'categoryID': 16, 'groupID': 6})
        self.dh.data['typefighterabils'].append(
            {'typeID': 1, 'abilityID': FighterAbilityId.autocannon})
        self.run_builder()
        self.assertEqual(len(self.types), 1)
        self.assertIn(1, self.types)
        self.assertEqual(len(self.types[1].abilities_data), 0)
        log = self.get_log(name=self.logger_name)
        self.assertEqual(len(log), 1)
        log_record = log[0]
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(
            log_record.msg,
            '1 rows contain abilities without effect, removing them')

    def test_cleaned(self):
        self.dh.data['evetypes'].append({'typeID': 1})
        self.dh.data['dgmtypeeffects'].append(
            {'typeID': 1, 'effectID': EffectId.fighter_ability_attack_m})
        self.dh.data['dgmeffects'].append(
            {'effectID': EffectId.fighter_ability_attack_m})
        self.dh.data['typefighterabils'].append(
            {'typeID': 1, 'abilityID': FighterAbilityId.autocannon})
        self.run_builder()
        self.assertEqual(len(self.types), 0)
        self.assertEqual(len(self.effects), 0)
        self.assertEqual(len(self.get_log(name=self.logger_name)), 0)
