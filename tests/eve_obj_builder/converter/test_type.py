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

from eos.const.eve import EffectId
from eos.const.eve import FighterAbilityId
from tests.eve_obj_builder.testcase import EveObjBuilderTestCase


class TestConversionType(EveObjBuilderTestCase):
    """Data should be saved into appropriate fields of an item type."""

    def test_fields(self):
        self.dh.data['evetypes'].append(
            {'randomField': 66, 'typeID': 1, 'groupID': 6})
        self.dh.data['evegroups'].append({'categoryID': 16, 'groupID': 6})
        self.dh.data['dgmtypeattribs'].append(
            {'typeID': 1, 'attributeID': 5, 'value': 10.0})
        self.dh.data['dgmtypeattribs'].append(
            {'attributeID': 80, 'typeID': 1, 'value': 180.0})
        self.dh.data['dgmtypeeffects'].append({
            'typeID': 1, 'effectID': EffectId.fighter_ability_attack_m,
            'isDefault': True})
        self.dh.data['dgmtypeeffects'].append({
            'typeID': 1, 'effectID': EffectId.fighter_ability_microwarpdrive,
            'isDefault': False})
        self.dh.data['dgmtypeeffects'].append({
            'typeID': 1, 'effectID': EffectId.fighter_ability_missiles,
            'isDefault': False})
        self.dh.data['dgmeffects'].append(
            {'effectID': EffectId.fighter_ability_attack_m})
        self.dh.data['dgmeffects'].append(
            {'effectID': EffectId.fighter_ability_microwarpdrive})
        self.dh.data['dgmeffects'].append(
            {'effectID': EffectId.fighter_ability_missiles})
        self.dh.data['typefighterabils'].append(
            {'typeID': 1, 'abilityID': FighterAbilityId.autocannon})
        self.dh.data['typefighterabils'].append({
            'typeID': 1, 'abilityID': FighterAbilityId.microwarpdrive,
            'cooldownSeconds': 60})
        self.dh.data['typefighterabils'].append({
            'typeID': 1, 'abilityID': FighterAbilityId.micromissile_swarm_exp,
            'chargeCount': 3})
        self.run_builder()
        self.assertEqual(len(self.types), 1)
        self.assertIn(1, self.types)
        item_type = self.types[1]
        self.assertEqual(item_type.group_id, 6)
        self.assertEqual(item_type.category_id, 16)
        type_attrs = item_type.attrs
        self.assertEqual(len(type_attrs), 2)
        self.assertEqual(type_attrs[5], 10.0)
        self.assertEqual(type_attrs[80], 180.0)
        type_effects = item_type.effects
        self.assertEqual(len(type_effects), 3)
        self.assertIn(EffectId.fighter_ability_attack_m, type_effects)
        self.assertIn(EffectId.fighter_ability_microwarpdrive, type_effects)
        self.assertIn(EffectId.fighter_ability_missiles, type_effects)
        type_defeff = item_type.default_effect
        self.assertEqual(type_defeff.id, EffectId.fighter_ability_attack_m)
        type_abilities_data = item_type.abilities_data
        self.assertEqual(len(type_abilities_data), 3)
        ability1_data = type_abilities_data[FighterAbilityId.autocannon]
        self.assertEqual(ability1_data.cooldown_time, 0)
        self.assertEqual(ability1_data.charge_quantity, math.inf)
        ability2_data = (
            type_abilities_data[FighterAbilityId.microwarpdrive])
        self.assertEqual(ability2_data.cooldown_time, 60)
        self.assertEqual(ability2_data.charge_quantity, math.inf)
        ability3_data = (
            type_abilities_data[FighterAbilityId.micromissile_swarm_exp])
        self.assertEqual(ability3_data.cooldown_time, 0)
        self.assertEqual(ability3_data.charge_quantity, 3)
