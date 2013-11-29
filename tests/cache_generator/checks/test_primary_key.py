#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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
#===============================================================================


from unittest.mock import patch

from eos.tests.cache_generator.generator_testcase import GeneratorTestCase
from eos.tests.environment import Logger


class TestPrimaryKey(GeneratorTestCase):
    """Check that only valid primary keys pass checks"""

    def test_single_proper_pk(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1, 'typeName': ''})
        self.dh.data['invtypes'].append({'typeID': 2, 'groupID': 1, 'typeName': ''})
        data = self.run_generator()
        self.assertEqual(len(self.log), 1)
        clean_stats = self.log[0]
        self.assertEqual(clean_stats.name, 'eos_test.cache_generator')
        self.assertEqual(clean_stats.levelno, Logger.INFO)
        self.assertIn(1, data['types'])
        self.assertIn(2, data['types'])

    def test_single_no_pk(self):
        self.dh.data['invtypes'].append({'groupID': 1, 'typeName': ''})
        data = self.run_generator()
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos_test.cache_generator')
        self.assertEqual(log_record.levelno, Logger.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table invtypes have invalid PKs, removing them')
        self.assertEqual(len(data['types']), 0)

    def test_single_invalid(self):
        self.dh.data['invtypes'].append({'typeID': 1.5, 'groupID': 1, 'typeName': ''})
        data = self.run_generator()
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos_test.cache_generator')
        self.assertEqual(log_record.levelno, Logger.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table invtypes have invalid PKs, removing them')
        self.assertEqual(len(data['types']), 0)

    def test_single_duplicate(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1, 'typeName': ''})
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 920, 'typeName': ''})
        data = self.run_generator()
        self.assertEqual(len(self.log), 2)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos_test.cache_generator')
        self.assertEqual(log_record.levelno, Logger.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table invtypes have invalid PKs, removing them')
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos_test.cache_generator')
        self.assertEqual(clean_stats.levelno, Logger.INFO)
        self.assertEqual(len(data['types']), 1)
        self.assertEqual(data['types'][1]['group_id'], 1)

    def test_single_duplicate_reverse(self):
        # Make sure first fed by data_handler row is accepted
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 920, 'typeName': ''})
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1, 'typeName': ''})
        data = self.run_generator()
        self.assertEqual(len(self.log), 2)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos_test.cache_generator')
        self.assertEqual(log_record.levelno, Logger.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table invtypes have invalid PKs, removing them')
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos_test.cache_generator')
        self.assertEqual(clean_stats.levelno, Logger.INFO)
        self.assertEqual(len(data['types']), 1)
        self.assertEqual(data['types'][1]['group_id'], 920)

    def test_single_cleaned(self):
        # Make sure check is ran before cleanup
        self.dh.data['invtypes'].append({'typeID': 1, 'typeName': ''})
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 920, 'typeName': ''})
        data = self.run_generator()
        self.assertEqual(len(self.log), 2)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos_test.cache_generator')
        self.assertEqual(log_record.levelno, Logger.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table invtypes have invalid PKs, removing them')
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos_test.cache_generator')
        self.assertEqual(clean_stats.levelno, Logger.INFO)
        self.assertEqual(len(data['types']), 0)

    def test_dual_proper_pk(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1, 'typeName': ''})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 100, 'value': 50.0})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 50, 'value': 100.0})
        data = self.run_generator()
        self.assertEqual(len(self.log), 1)
        clean_stats = self.log[0]
        self.assertEqual(clean_stats.name, 'eos_test.cache_generator')
        self.assertEqual(clean_stats.levelno, Logger.INFO)
        type_attributes = data['types'][1]['attributes']
        self.assertEqual(type_attributes[100], 50.0)
        self.assertEqual(type_attributes[50], 100.0)

    def test_dual_no_pk(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1, 'typeName': ''})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'value': 50.0})
        data = self.run_generator()
        self.assertEqual(len(self.log), 2)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos_test.cache_generator')
        self.assertEqual(log_record.levelno, Logger.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table dgmtypeattribs have invalid PKs, removing them')
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos_test.cache_generator')
        self.assertEqual(clean_stats.levelno, Logger.INFO)
        self.assertEqual(len(data['types'][1]['attributes']), 0)

    def test_dual_invalid(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1, 'typeName': ''})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 100.1, 'value': 50.0})
        data = self.run_generator()
        self.assertEqual(len(self.log), 2)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos_test.cache_generator')
        self.assertEqual(log_record.levelno, Logger.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table dgmtypeattribs have invalid PKs, removing them')
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos_test.cache_generator')
        self.assertEqual(clean_stats.levelno, Logger.INFO)
        self.assertEqual(len(data['types'][1]['attributes']), 0)

    def test_dual_duplicate(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1, 'typeName': ''})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 100, 'value': 50.0})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 100, 'value': 5.0})
        data = self.run_generator()
        self.assertEqual(len(self.log), 2)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos_test.cache_generator')
        self.assertEqual(log_record.levelno, Logger.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table dgmtypeattribs have invalid PKs, removing them')
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos_test.cache_generator')
        self.assertEqual(clean_stats.levelno, Logger.INFO)
        type_attributes = data['types'][1]['attributes']
        self.assertEqual(len(type_attributes), 1)
        self.assertEqual(type_attributes[100], 50.0)

    def test_dual_cleaned(self):
        # Make sure check is ran before cleanup
        self.dh.data['invtypes'].append({'typeID': 1, 'typeName': ''})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 100, 'value': 50.0})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 100, 'value': 5.0})
        data = self.run_generator()
        self.assertEqual(len(self.log), 2)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos_test.cache_generator')
        self.assertEqual(log_record.levelno, Logger.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table dgmtypeattribs have invalid PKs, removing them')
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos_test.cache_generator')
        self.assertEqual(clean_stats.levelno, Logger.INFO)
        self.assertEqual(len(data['types']), 0)

    def test_dual_duplicate_reverse(self):
        # Make sure first fed by data_handler row is accepted
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1, 'typeName': ''})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 100, 'value': 5.0})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 100, 'value': 50.0})
        data = self.run_generator()
        self.assertEqual(len(self.log), 2)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos_test.cache_generator')
        self.assertEqual(log_record.levelno, Logger.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table dgmtypeattribs have invalid PKs, removing them')
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos_test.cache_generator')
        self.assertEqual(clean_stats.levelno, Logger.INFO)
        type_attributes = data['types'][1]['attributes']
        self.assertEqual(len(type_attributes), 1)
        self.assertEqual(type_attributes[100], 5.0)

    # Now, when PK-related checks cover invtypes (single PK)
    # and dgmtypeattribs (dual PK) tables, run simple tests on
    # the rest of the tables to make sure they are covered
    def test_invgroups(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1, 'typeName': ''})
        self.dh.data['invgroups'].append({'groupID': 1, 'categoryID': 7, 'groupName': ''})
        self.dh.data['invgroups'].append({'groupID': 1, 'categoryID': 32, 'groupName': ''})
        data = self.run_generator()
        self.assertEqual(len(self.log), 2)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos_test.cache_generator')
        self.assertEqual(log_record.levelno, Logger.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table invgroups have invalid PKs, removing them')
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos_test.cache_generator')
        self.assertEqual(clean_stats.levelno, Logger.INFO)
        self.assertEqual(len(data['types']), 1)
        self.assertEqual(data['types'][1]['category_id'], 7)

    def test_dgmattribs(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1, 'typeName': ''})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 7, 'value': 8.0})
        self.dh.data['dgmattribs'].append({'attributeID': 7, 'maxAttributeID': 50, 'attributeName': ''})
        self.dh.data['dgmattribs'].append({'attributeID': 7, 'maxAttributeID': 55, 'attributeName': ''})
        data = self.run_generator()
        self.assertEqual(len(self.log), 2)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos_test.cache_generator')
        self.assertEqual(log_record.levelno, Logger.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table dgmattribs have invalid PKs, removing them')
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos_test.cache_generator')
        self.assertEqual(clean_stats.levelno, Logger.INFO)
        self.assertEqual(len(data['attributes']), 1)
        self.assertEqual(data['attributes'][7]['max_attribute_id'], 50)

    def test_dgmeffects(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1, 'typeName': ''})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 7, 'isDefault': False})
        self.dh.data['dgmeffects'].append({'effectID': 7, 'effectCategory': 50})
        self.dh.data['dgmeffects'].append({'effectID': 7, 'effectCategory': 55})
        data = self.run_generator()
        self.assertEqual(len(self.log), 2)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos_test.cache_generator')
        self.assertEqual(log_record.levelno, Logger.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table dgmeffects have invalid PKs, removing them')
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos_test.cache_generator')
        self.assertEqual(clean_stats.levelno, Logger.INFO)
        self.assertEqual(len(data['effects']), 1)
        self.assertEqual(data['effects'][7]['effect_category'], 50)

    def test_dgmtypeeffects(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1, 'typeName': ''})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 100, 'isDefault': True})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 100, 'isDefault': False})
        self.dh.data['dgmeffects'].append({'effectID': 100, 'falloffAttributeID': 70})
        data = self.run_generator()
        self.assertEqual(len(self.log), 2)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos_test.cache_generator')
        self.assertEqual(log_record.levelno, Logger.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table dgmtypeeffects have invalid PKs, removing them')
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos_test.cache_generator')
        self.assertEqual(clean_stats.levelno, Logger.INFO)
        self.assertEqual(len(data['types']), 1)
        self.assertEqual(data['types'][1]['falloff_attribute_id'], 70)

    @patch('eos.data.cache_generator.converter.ModifierBuilder')
    def test_dgmexpressions(self, mod_builder):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1, 'typeName': ''})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 7, 'isDefault': False})
        self.dh.data['dgmeffects'].append({'effectID': 7, 'preExpression': 62, 'postExpression': 83})
        self.dh.data['dgmexpressions'].append({'expressionID': 83, 'operandID': 75, 'arg1': 1009, 'arg2': 15,
                                               'expressionValue': None, 'expressionTypeID': 502,
                                               'expressionGroupID': 451, 'expressionAttributeID': 90})
        self.dh.data['dgmexpressions'].append({'expressionID': 83, 'operandID': 80, 'arg1': 1009, 'arg2': 15,
                                               'expressionValue': None, 'expressionTypeID': 502,
                                               'expressionGroupID': 451, 'expressionAttributeID': 90})
        mod_builder.return_value.build_effect.return_value = ([], 0)
        self.run_generator()
        self.assertEqual(len(self.log), 2)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos_test.cache_generator')
        self.assertEqual(log_record.levelno, Logger.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table dgmexpressions have invalid PKs, removing them')
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos_test.cache_generator')
        self.assertEqual(clean_stats.levelno, Logger.INFO)
        expressions = mod_builder.mock_calls[0][1][0]
        self.assertEqual(len(expressions), 1)
        expected = {'expressionID': 83, 'operandID': 75, 'arg1': 1009, 'arg2': 15,
                    'expressionValue': None, 'expressionTypeID': 502,
                    'expressionGroupID': 451, 'expressionAttributeID': 90}
        # Filter out service fields
        actual = dict((k, expressions[0][k]) for k in filter(lambda k: k in expected, expressions[0]))
        self.assertEqual(actual, expected)
