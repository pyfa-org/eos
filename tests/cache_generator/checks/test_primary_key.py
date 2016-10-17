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


class TestPrimaryKey(GeneratorTestCase):
    """Check that only valid primary keys pass checks"""

    def test_single_proper_pk(self):
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1, 'typeName_en-us': ''})
        self.dh.data['evetypes'].append({'typeID': 2, 'groupID': 1, 'typeName_en-us': ''})
        data = self.run_generator()
        self.assertEqual(len(self.log), 2)
        literal_stats = self.log[0]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertIn(1, data['types'])
        self.assertIn(2, data['types'])

    def test_single_no_pk(self):
        self.dh.data['evetypes'].append({'groupID': 1, 'typeName_en-us': ''})
        data = self.run_generator()
        self.assertEqual(len(self.log), 2)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.checker')
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table evetypes have invalid PKs, removing them')
        literal_stats = self.log[1]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        self.assertEqual(len(data['types']), 0)

    def test_single_invalid(self):
        self.dh.data['evetypes'].append({'typeID': 1.5, 'groupID': 1, 'typeName_en-us': ''})
        data = self.run_generator()
        self.assertEqual(len(self.log), 2)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.checker')
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table evetypes have invalid PKs, removing them')
        literal_stats = self.log[1]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        self.assertEqual(len(data['types']), 0)

    def test_single_duplicate(self):
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1, 'typeName_en-us': ''})
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 920, 'typeName_en-us': ''})
        data = self.run_generator()
        self.assertEqual(len(self.log), 3)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.checker')
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table evetypes have invalid PKs, removing them')
        literal_stats = self.log[1]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        clean_stats = self.log[2]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertEqual(len(data['types']), 1)
        self.assertEqual(data['types'][1]['group'], 1)

    def test_single_duplicate_reverse(self):
        # Make sure first fed by data_handler row is accepted
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 920, 'typeName_en-us': ''})
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1, 'typeName_en-us': ''})
        data = self.run_generator()
        self.assertEqual(len(self.log), 3)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.checker')
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table evetypes have invalid PKs, removing them')
        literal_stats = self.log[1]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        clean_stats = self.log[2]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertEqual(len(data['types']), 1)
        self.assertEqual(data['types'][1]['group'], 920)

    def test_single_cleaned(self):
        # Make sure check is ran before cleanup
        self.dh.data['evetypes'].append({'typeID': 1, 'typeName_en-us': ''})
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 920, 'typeName_en-us': ''})
        data = self.run_generator()
        self.assertEqual(len(self.log), 3)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.checker')
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table evetypes have invalid PKs, removing them')
        literal_stats = self.log[1]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        clean_stats = self.log[2]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertEqual(len(data['types']), 0)

    def test_dual_proper_pk(self):
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1, 'typeName_en-us': ''})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 100, 'value': 50.0})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 50, 'value': 100.0})
        data = self.run_generator()
        self.assertEqual(len(self.log), 2)
        literal_stats = self.log[0]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        type_attributes = data['types'][1]['attributes']
        self.assertEqual(type_attributes[100], 50.0)
        self.assertEqual(type_attributes[50], 100.0)

    def test_dual_no_pk(self):
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1, 'typeName_en-us': ''})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'value': 50.0})
        data = self.run_generator()
        self.assertEqual(len(self.log), 3)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.checker')
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table dgmtypeattribs have invalid PKs, removing them')
        literal_stats = self.log[1]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        clean_stats = self.log[2]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertEqual(len(data['types'][1]['attributes']), 0)

    def test_dual_invalid(self):
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1, 'typeName_en-us': ''})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 100.1, 'value': 50.0})
        data = self.run_generator()
        self.assertEqual(len(self.log), 3)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.checker')
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table dgmtypeattribs have invalid PKs, removing them')
        literal_stats = self.log[1]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        clean_stats = self.log[2]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertEqual(len(data['types'][1]['attributes']), 0)

    def test_dual_duplicate(self):
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1, 'typeName_en-us': ''})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 100, 'value': 50.0})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 100, 'value': 5.0})
        data = self.run_generator()
        self.assertEqual(len(self.log), 3)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.checker')
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table dgmtypeattribs have invalid PKs, removing them')
        literal_stats = self.log[1]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        clean_stats = self.log[2]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        type_attributes = data['types'][1]['attributes']
        self.assertEqual(len(type_attributes), 1)
        self.assertEqual(type_attributes[100], 50.0)

    def test_dual_cleaned(self):
        # Make sure check is ran before cleanup
        self.dh.data['evetypes'].append({'typeID': 1, 'typeName_en-us': ''})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 100, 'value': 50.0})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 100, 'value': 5.0})
        data = self.run_generator()
        self.assertEqual(len(self.log), 3)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.checker')
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table dgmtypeattribs have invalid PKs, removing them')
        literal_stats = self.log[1]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        clean_stats = self.log[2]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertEqual(len(data['types']), 0)

    def test_dual_duplicate_reverse(self):
        # Make sure first fed by data_handler row is accepted
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1, 'typeName_en-us': ''})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 100, 'value': 5.0})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 100, 'value': 50.0})
        data = self.run_generator()
        self.assertEqual(len(self.log), 3)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.checker')
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table dgmtypeattribs have invalid PKs, removing them')
        literal_stats = self.log[1]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        clean_stats = self.log[2]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        type_attributes = data['types'][1]['attributes']
        self.assertEqual(len(type_attributes), 1)
        self.assertEqual(type_attributes[100], 5.0)

    # Now, when PK-related checks cover evetypes (single PK)
    # and dgmtypeattribs (dual PK) tables, run simple tests on
    # the rest of the tables to make sure they are covered
    def test_evegroups(self):
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1, 'typeName_en-us': ''})
        self.dh.data['evegroups'].append({'groupID': 1, 'categoryID': 7, 'groupName_en-us': ''})
        self.dh.data['evegroups'].append({'groupID': 1, 'categoryID': 32, 'groupName_en-us': ''})
        data = self.run_generator()
        self.assertEqual(len(self.log), 3)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.checker')
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table evegroups have invalid PKs, removing them')
        literal_stats = self.log[1]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        clean_stats = self.log[2]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertEqual(len(data['types']), 1)
        self.assertEqual(data['types'][1]['category'], 7)

    def test_dgmattribs(self):
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1, 'typeName_en-us': ''})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 7, 'value': 8.0})
        self.dh.data['dgmattribs'].append({'attributeID': 7, 'maxAttributeID': 50, 'attributeName': ''})
        self.dh.data['dgmattribs'].append({'attributeID': 7, 'maxAttributeID': 55, 'attributeName': ''})
        data = self.run_generator()
        self.assertEqual(len(self.log), 3)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.checker')
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table dgmattribs have invalid PKs, removing them')
        literal_stats = self.log[1]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        clean_stats = self.log[2]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertEqual(len(data['attributes']), 1)
        self.assertEqual(data['attributes'][7]['max_attribute'], 50)

    def test_dgmeffects(self):
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1, 'typeName_en-us': ''})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 7, 'isDefault': False})
        self.dh.data['dgmeffects'].append({'effectID': 7, 'effectCategory': 50})
        self.dh.data['dgmeffects'].append({'effectID': 7, 'effectCategory': 55})
        data = self.run_generator()
        self.assertEqual(len(self.log), 3)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.checker')
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table dgmeffects have invalid PKs, removing them')
        literal_stats = self.log[1]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        clean_stats = self.log[2]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertEqual(len(data['effects']), 1)
        self.assertEqual(data['effects'][7]['effect_category'], 50)

    def test_dgmtypeeffects(self):
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1, 'typeName_en-us': ''})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 100, 'isDefault': True})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 100, 'isDefault': False})
        self.dh.data['dgmeffects'].append({'effectID': 100})
        data = self.run_generator()
        self.assertEqual(len(self.log), 3)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.checker')
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table dgmtypeeffects have invalid PKs, removing them')
        literal_stats = self.log[1]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        clean_stats = self.log[2]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertEqual(len(data['types']), 1)
        self.assertEqual(data['types'][1]['default_effect'], 100)

    @patch('eos.data.cache_generator.converter.ModifierBuilder')
    def test_dgmexpressions(self, mod_builder):
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1, 'typeName_en-us': ''})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 7, 'isDefault': False})
        self.dh.data['dgmeffects'].append({'effectID': 7, 'preExpression': 62, 'postExpression': 83})
        self.dh.data['dgmexpressions'].append({
            'expressionID': 83, 'operandID': 75, 'arg1': 1009, 'arg2': 15,
            'expressionValue': None, 'expressionTypeID': 502,
            'expressionGroupID': 451, 'expressionAttributeID': 90
        })
        self.dh.data['dgmexpressions'].append({
            'expressionID': 83, 'operandID': 80, 'arg1': 1009, 'arg2': 15,
            'expressionValue': None, 'expressionTypeID': 502,
            'expressionGroupID': 451, 'expressionAttributeID': 90
        })
        mod_builder.return_value.build.return_value = ([], 0)
        self.run_generator()
        self.assertEqual(len(self.log), 3)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.checker')
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(log_record.msg, '1 rows in table dgmexpressions have invalid PKs, removing them')
        literal_stats = self.log[1]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        clean_stats = self.log[2]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        expressions = mod_builder.mock_calls[0][1][0]
        self.assertEqual(len(expressions), 1)
        expected = {
            'expressionID': 83, 'operandID': 75, 'arg1': 1009, 'arg2': 15,
            'expressionValue': None, 'expressionTypeID': 502,
            'expressionGroupID': 451, 'expressionAttributeID': 90
        }
        # Filter out fields we do not want to check
        actual = dict((k, expressions[0][k]) for k in filter(lambda k: k in expected, expressions[0]))
        self.assertEqual(actual, expected)
