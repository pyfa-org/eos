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


from tests.eve_obj_builder.testcase import EveObjBuilderTestCase


class TestConversionType(EveObjBuilderTestCase):
    """Data should be saved into appropriate fields of an item type."""

    logger_name = 'eos.data.eve_obj_builder.converter'

    def test_fields(self):
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
            {'typeID': 1, 'slot': 'abilitySlot1', 'abilityID': 5})
        self.dh.data['typefighterabils'].append({
            'typeID': 1, 'slot': 'abilitySlot2', 'abilityID': 6,
            'cooldownSeconds': 60})
        self.dh.data['typefighterabils'].append({
            'typeID': 1, 'slot': 'abilitySlot33', 'abilityID': 50,
            'chargeCount': 3, 'rearmTimeSeconds': 20})
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
        type_fighterabils = item_type.fighter_abilities
        self.assertEqual(len(type_fighterabils), 3)
        self.assertCountEqual(type_fighterabils, {5, 6, 50})
        self.assertDictEqual(type_fighterabils[5], {
            'cooldown_time': None, 'charge_quantity': None,
            'charge_rearm_time': None})
        self.assertDictEqual(type_fighterabils[6], {
            'cooldown_time': 60, 'charge_quantity': None,
            'charge_rearm_time': None})
        self.assertDictEqual(type_fighterabils[50], {
            'cooldown_time': None, 'charge_quantity': 3,
            'charge_rearm_time': 20})
        self.assertEqual(len(self.get_log(name=self.logger_name)), 0)
