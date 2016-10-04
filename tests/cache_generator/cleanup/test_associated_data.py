# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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
# ===============================================================================


import logging
from unittest.mock import patch

from tests.cache_generator.generator_testcase import GeneratorTestCase


@patch('eos.data.cache_generator.converter.ModifierBuilder')
class TestAssociatedData(GeneratorTestCase):
    """
    Check that types, which passed filter, pull in
    all related data.
    """

    def __generate_data(self):
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 5, 'value': 10.0})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 200, 'isDefault': True})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 201, 'isDefault': False})
        self.dh.data['dgmeffects'].append({
            'effectID': 200, 'effectCategory': 26, 'isOffensive': True, 'isAssistance': False,
            'fittingUsageChanceAttributeID': 1000, 'preExpression': 100, 'postExpression': 101,
            'durationAttributeID': 1001, 'dischargeAttributeID': 1002, 'rangeAttributeID': 1003,
            'falloffAttributeID': 1004, 'trackingSpeedAttributeID': 1005, 'modifierInfo': None
        })
        self.dh.data['dgmeffects'].append({
            'effectID': 201, 'effectCategory': 33, 'isOffensive': False, 'isAssistance': False,
            'fittingUsageChanceAttributeID': None, 'preExpression': None, 'postExpression': None,
            'durationAttributeID': None, 'dischargeAttributeID': None, 'rangeAttributeID': None,
            'falloffAttributeID': None, 'trackingSpeedAttributeID': None,
            'modifierInfo': ('- domain: shipID\n  func: LocationRequiredSkillModifier\n  modifiedAttributeID: 1009\n'
                '  modifyingAttributeID: 1008\n  operator: 6\n  skillTypeID: 3\n- domain: shipID\n'
                '  func: LocationGroupModifier\n  groupID: 501\n  modifiedAttributeID: 1008\n'
                '  modifyingAttributeID: 1009\n  operator: 6\n')
        })
        self.dh.data['dgmattribs'].append({
            'attributeID': 5, 'maxAttributeID': 1006, 'defaultValue': 0.0,
            'highIsGood': False, 'stackable': True, 'attributeName': ''
        })
        self.dh.data['dgmattribs'].append({
            'attributeID': 1000, 'maxAttributeID': None, 'defaultValue': 0.0,
            'highIsGood': False, 'stackable': False, 'attributeName': ''
        })
        self.dh.data['dgmattribs'].append({
            'attributeID': 1001, 'maxAttributeID': None, 'defaultValue': 0.0,
            'highIsGood': False, 'stackable': False, 'attributeName': ''
        })
        self.dh.data['dgmattribs'].append({
            'attributeID': 1002, 'maxAttributeID': None, 'defaultValue': 0.0,
            'highIsGood': False, 'stackable': False, 'attributeName': ''
        })
        self.dh.data['dgmattribs'].append({
            'attributeID': 1003, 'maxAttributeID': None, 'defaultValue': 0.0,
            'highIsGood': False, 'stackable': False, 'attributeName': ''
        })
        self.dh.data['dgmattribs'].append({
            'attributeID': 1004, 'maxAttributeID': None, 'defaultValue': 0.0,
            'highIsGood': False, 'stackable': False, 'attributeName': ''
        })
        self.dh.data['dgmattribs'].append({
            'attributeID': 1005, 'maxAttributeID': None, 'defaultValue': 0.0,
            'highIsGood': False, 'stackable': False, 'attributeName': ''
        })
        self.dh.data['dgmattribs'].append({
            'attributeID': 1006, 'maxAttributeID': None, 'defaultValue': 0.0,
            'highIsGood': False, 'stackable': False, 'attributeName': ''
        })
        self.dh.data['dgmexpressions'].append({
            'expressionID': 100, 'operandID': 6, 'arg1': 102, 'arg2': 103,
            'expressionValue': None, 'expressionTypeID': 2,
            'expressionGroupID': 500, 'expressionAttributeID': 1007
        })
        self.dh.data['dgmexpressions'].append({
            'expressionID': 101, 'operandID': 6, 'arg1': 102, 'arg2': 103,
            'expressionValue': None, 'expressionTypeID': None,
            'expressionGroupID': None, 'expressionAttributeID': None
        })
        self.dh.data['dgmexpressions'].append({
            'expressionID': 102, 'operandID': 6, 'arg1': None, 'arg2': None,
            'expressionValue': None, 'expressionTypeID': None,
            'expressionGroupID': None, 'expressionAttributeID': None
        })
        self.dh.data['dgmexpressions'].append({
            'expressionID': 103, 'operandID': 6, 'arg1': None, 'arg2': None,
            'expressionValue': None, 'expressionTypeID': None,
            'expressionGroupID': None, 'expressionAttributeID': None
        })
        # Weak entities in any case, but linked through expression
        self.dh.data['evetypes'].append({'typeID': 2, 'groupID': 6, 'typeName_en-us': ''})
        self.dh.data['evegroups'].append({'groupID': 6, 'categoryID': 50, 'groupName_en-us': ''})
        self.dh.data['dgmattribs'].append({
            'attributeID': 1007, 'maxAttributeID': None, 'default_value': 0.0,
            'high_is_good': False, 'stackable': False, 'attributeName': ''
        })
        # Also weak entities, but linked through modifier info
        self.dh.data['evetypes'].append({'typeID': 3, 'groupID': 7, 'typeName_en-us': ''})
        self.dh.data['evegroups'].append({'groupID': 7, 'categoryID': 51, 'groupName_en-us': ''})
        self.dh.data['dgmattribs'].append({
            'attributeID': 1008, 'maxAttributeID': None, 'default_value': 0.0,
            'high_is_good': False, 'stackable': False, 'attributeName': ''
        })
        self.dh.data['dgmattribs'].append({
            'attributeID': 1009, 'maxAttributeID': None, 'default_value': 0.0,
            'high_is_good': False, 'stackable': False, 'attributeName': ''
        })

    def test_strong(self, mod_builder):
        self.__generate_data()
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 5, 'typeName_en-us': ''})
        self.dh.data['evegroups'].append({'groupID': 5, 'categoryID': 16, 'groupName_en-us': ''})
        mod_builder.return_value.build.return_value = ([], 0)
        data = self.run_generator()
        self.assertEqual(len(self.log), 2)
        literal_stats = self.log[0]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertEqual(
            clean_stats.msg,
            'cleaned: 0.0% from dgmattribs, 0.0% from dgmeffects, 0.0% from dgmexpressions, '
            '0.0% from dgmtypeattribs, 0.0% from dgmtypeeffects, 0.0% from evegroups, 0.0% from evetypes'
        )
        self.assertEqual(len(data['types']), 3)
        self.assertIn(1, data['types'])
        self.assertEqual(data['types'][1]['category'], 16)
        self.assertIn(2, data['types'])
        self.assertEqual(data['types'][2]['category'], 50)
        self.assertIn(3, data['types'])
        self.assertEqual(data['types'][3]['category'], 51)
        self.assertEqual(len(data['attributes']), 11)
        self.assertIn(5, data['attributes'])
        self.assertIn(1000, data['attributes'])
        self.assertIn(1001, data['attributes'])
        self.assertIn(1002, data['attributes'])
        self.assertIn(1003, data['attributes'])
        self.assertIn(1004, data['attributes'])
        self.assertIn(1005, data['attributes'])
        self.assertIn(1006, data['attributes'])
        self.assertIn(1007, data['attributes'])
        self.assertIn(1008, data['attributes'])
        self.assertIn(1009, data['attributes'])
        self.assertEqual(len(data['effects']), 2)
        self.assertIn(200, data['effects'])
        self.assertIn(201, data['effects'])
        expressions = mod_builder.mock_calls[0][1][0]
        self.assertEqual(len(expressions), 4)
        expression_ids = set(row['expressionID'] for row in expressions)
        self.assertEqual(expression_ids, {100, 101, 102, 103})

    def test_weak(self, mod_builder):
        self.__generate_data()
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 5, 'typeName_en-us': ''})
        self.dh.data['evegroups'].append({'groupID': 5, 'categoryID': 101, 'groupName_en-us': ''})
        mod_builder.return_value.build.return_value = ([], 0)
        data = self.run_generator()
        self.assertEqual(len(self.log), 2)
        literal_stats = self.log[0]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertEqual(clean_stats.msg,
            'cleaned: 100.0% from dgmattribs, 100.0% from dgmeffects, 100.0% from dgmexpressions, '
            '100.0% from dgmtypeattribs, 100.0% from dgmtypeeffects, 100.0% from evegroups, '
            '100.0% from evetypes'
        )
        self.assertEqual(len(data['types']), 0)
        self.assertEqual(len(data['attributes']), 0)
        self.assertEqual(len(data['effects']), 0)
        self.assertEqual(len(mod_builder.mock_calls[0][1][0]), 0)

    def test_unlinked(self, mod_builder):
        self.__generate_data()
        data = self.run_generator()
        self.assertEqual(len(self.log), 2)
        literal_stats = self.log[0]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertEqual(
            clean_stats.msg,
            'cleaned: 100.0% from dgmattribs, 100.0% from dgmeffects, 100.0% from dgmexpressions, '
            '100.0% from dgmtypeattribs, 100.0% from dgmtypeeffects, 100.0% from evegroups, '
            '100.0% from evetypes'
        )
        self.assertEqual(len(data['types']), 0)
        self.assertEqual(len(data['attributes']), 0)
        self.assertEqual(len(data['effects']), 0)
        self.assertEqual(len(mod_builder.mock_calls[0][1][0]), 0)

    def test_reverse_types(self, mod_builder):
        # Check that single type included into table does not
        # pull other types belonging to same group
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 5, 'typeName_en-us': ''})
        self.dh.data['evegroups'].append({'groupID': 5, 'categoryID': 16, 'groupName_en-us': ''})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 100, 'isDefault': True})
        self.dh.data['dgmeffects'].append({
            'effectID': 100, 'effectCategory': 8888, 'isOffensive': True, 'isAssistance': False,
            'fittingUsageChanceAttributeID': None, 'preExpression': 101, 'postExpression': None,
            'durationAttributeID': None, 'dischargeAttributeID': None, 'rangeAttributeID': None,
            'falloffAttributeID': None, 'trackingSpeedAttributeID': None,
            'modifierInfo': '- domain: shipID\n  func: LocationRequiredSkillModifier\n'
                '  modifiedAttributeID: 1009\n  modifyingAttributeID: 1008\n  operator: 6\n'
                '  skillTypeID: 3\n'
        })
        self.dh.data['dgmexpressions'].append({
            'expressionID': 101, 'operandID': 6, 'arg1': None, 'arg2': None,
            'expressionValue': None, 'expressionTypeID': 2,
            'expressionGroupID': None, 'expressionAttributeID': None
        })
        # 2 weak type, but linked through expression/YAML
        self.dh.data['evetypes'].append({'typeID': 2, 'groupID': 6, 'typeName_en-us': ''})
        self.dh.data['evetypes'].append({'typeID': 3, 'groupID': 6, 'typeName_en-us': ''})
        self.dh.data['evetypes'].append({'typeID': 4, 'groupID': 6, 'typeName_en-us': ''})
        self.dh.data['evegroups'].append({'groupID': 6, 'categoryID': 50, 'groupName_en-us': ''})
        mod_builder.return_value.build.return_value = ([], 0)
        data = self.run_generator()
        self.assertEqual(len(self.log), 2)
        literal_stats = self.log[0]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertEqual(
            clean_stats.msg,
            'cleaned: 0.0% from dgmeffects, 0.0% from dgmexpressions, 0.0% from dgmtypeeffects, '
            '0.0% from evegroups, 25.0% from evetypes'
        )
        self.assertEqual(len(data['types']), 3)
        self.assertIn(1, data['types'])
        self.assertIn(2, data['types'])
        self.assertIn(3, data['types'])
        self.assertEqual(len(data['attributes']), 0)
        self.assertEqual(len(data['effects']), 1)
        self.assertIn(100, data['effects'])
        expressions = mod_builder.mock_calls[0][1][0]
        self.assertEqual(len(expressions), 1)
        expression_ids = set(row['expressionID'] for row in expressions)
        self.assertEqual(expression_ids, {101})
