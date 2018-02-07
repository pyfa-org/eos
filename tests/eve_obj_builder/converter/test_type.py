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

from eos.const.eve import FighterAbilityId
from tests.eve_obj_builder.testcase import EveObjBuilderTestCase


class TestConversionType(EveObjBuilderTestCase):
    """Data should be saved into appropriate fields of an item type."""

    logger_name = 'eos.data.eve_obj_builder.converter'

    def test_fields(self):
        attack1_aid = FighterAbilityId.autocannon
        attack2_aid = FighterAbilityId.microwarpdrive
        mwd_aid = FighterAbilityId.micromissile_swarm_exp
        self.dh.data['evetypes'].append(
            {'randomField': 66, 'typeID': 1, 'groupID': 6})
        self.dh.data['evegroups'].append({'categoryID': 16, 'groupID': 6})
        self.dh.data['dgmtypeattribs'].append(
            {'typeID': 1, 'attributeID': 5, 'value': 10.0})
        self.dh.data['dgmtypeattribs'].append(
            {'attributeID': 80, 'typeID': 1, 'value': 180.0})
        self.dh.data['dgmtypeeffects'].append(
            {'typeID': 1, 'effectID': 111, 'isDefault': True})
        self.dh.data['dgmtypeeffects'].append(
            {'typeID': 1, 'effectID': 1111, 'isDefault': False})
        self.dh.data['dgmeffects'].append({
            'effectID': 111, 'effectCategory': 8, 'isOffensive': True,
            'isAssistance': False, 'fittingUsageChanceAttributeID': 96,
            'preExpression': None, 'postExpression': None})
        self.dh.data['dgmeffects'].append({
            'effectID': 1111, 'effectCategory': 85, 'isOffensive': False,
            'isAssistance': True, 'fittingUsageChanceAttributeID': 41,
            'preExpression': None, 'postExpression': None})
        self.dh.data['typefighterabils'].append(
            {'typeID': 1, 'abilityID': attack1_aid})
        self.dh.data['typefighterabils'].append(
            {'typeID': 1, 'abilityID': mwd_aid, 'cooldownSeconds': 60})
        self.dh.data['typefighterabils'].append(
            {'typeID': 1, 'abilityID': attack2_aid, 'chargeCount': 3})
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
        self.assertEqual(len(type_effects), 2)
        self.assertIn(111, type_effects)
        self.assertIn(1111, type_effects)
        type_defeff = item_type.default_effect
        self.assertEqual(type_defeff.id, 111)
        type_abilities_data = item_type.abilities_data
        self.assertEqual(len(type_abilities_data), 3)
        attack1_adata = type_abilities_data[attack1_aid]
        self.assertEqual(attack1_adata.cooldown_time, 0)
        self.assertEqual(attack1_adata.charge_quantity, math.inf)
        attack2_adata = type_abilities_data[attack2_aid]
        self.assertEqual(attack2_adata.cooldown_time, 0)
        self.assertEqual(attack2_adata.charge_quantity, 3)
        mwd_adata = type_abilities_data[mwd_aid]
        self.assertEqual(mwd_adata.cooldown_time, 60)
        self.assertEqual(mwd_adata.charge_quantity, math.inf)
