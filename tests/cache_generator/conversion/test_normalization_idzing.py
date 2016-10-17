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

from eos.const.eve import Operand
from tests.cache_generator.generator_testcase import GeneratorTestCase


@patch('eos.data.cache_generator.converter.ModifierBuilder')
class TestNormalizationIdzing(GeneratorTestCase):
    """Check that conversion of symbolic references to IDs functions."""

    def test_type_idzing(self, mod_builder):
        self.dh.data['evetypes'].append({'typeID': 556, 'groupID': 1, 'typeName_en-us': 'Big Gun 3'})
        self.dh.data['dgmtypeeffects'].append({'typeID': 556, 'effectID': 111})
        self.dh.data['dgmeffects'].append({'effectID': 111, 'preExpression': 57, 'postExpression': 57})
        self.dh.data['dgmexpressions'].append({
            'expressionID': 57, 'operandID': Operand.def_type, 'arg1': 5007,
            'arg2': 66, 'expressionValue': 'BigGun3', 'expressionTypeID': None,
            'expressionGroupID': 567, 'expressionAttributeID': 102
        })
        mod_builder.return_value.build.return_value = ([], 0)
        self.run_generator()
        self.assertEqual(len(self.log), 2)
        literal_stats = self.log[0]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        self.assertEqual(
            literal_stats.msg, 'conversion of literal references to IDs in dgmexpressions: 1 successful, 0 failed')
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        # As in expression conversion, we're verifying expressions
        # passed to modifier builder, as it's much easier to do
        expressions = mod_builder.mock_calls[0][1][0]
        self.assertEqual(len(expressions), 1)
        expected = {
            'expressionID': 57, 'operandID': Operand.def_type, 'arg1': 5007, 'arg2': 66,
            'expressionValue': None, 'expressionTypeID': 556, 'expressionGroupID': 567,
            'expressionAttributeID': 102, 'table_pos': 0
        }
        self.assertIn(expected, expressions)

    def test_group_idzing(self, mod_builder):
        self.dh.data['evetypes'].append({'typeID': 556, 'groupID': 668, 'typeName_en-us': ''})
        self.dh.data['evegroups'].append({'groupID': 668, 'categoryID': 16, 'groupName_en-us': 'Big Guns'})
        self.dh.data['dgmtypeeffects'].append({'typeID': 556, 'effectID': 111})
        self.dh.data['dgmeffects'].append({'effectID': 111, 'preExpression': 57, 'postExpression': 57})
        self.dh.data['dgmexpressions'].append({
            'expressionID': 57, 'operandID': Operand.def_grp, 'arg1': 5007,
            'arg2': 66, 'expressionValue': 'BigGuns', 'expressionTypeID': 567,
            'expressionGroupID': None, 'expressionAttributeID': 102
        })
        mod_builder.return_value.build.return_value = ([], 0)
        self.run_generator()
        self.assertEqual(len(self.log), 2)
        literal_stats = self.log[0]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        self.assertEqual(
            literal_stats.msg, 'conversion of literal references to IDs in dgmexpressions: 1 successful, 0 failed')
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        expressions = mod_builder.mock_calls[0][1][0]
        self.assertEqual(len(expressions), 1)
        expected = {
            'expressionID': 57, 'operandID': Operand.def_grp, 'arg1': 5007, 'arg2': 66,
            'expressionValue': None, 'expressionTypeID': 567, 'expressionGroupID': 668,
            'expressionAttributeID': 102, 'table_pos': 0
        }
        self.assertIn(expected, expressions)

    def test_attribute_idzing(self, mod_builder):
        self.dh.data['evetypes'].append({'typeID': 556, 'groupID': 668, 'typeName_en-us': ''})
        self.dh.data['evegroups'].append({'groupID': 668, 'categoryID': 16, 'groupName_en-us': ''})
        self.dh.data['dgmtypeattribs'].append({'typeID': 556, 'attributeID': 334, 'value': 2})
        self.dh.data['dgmattribs'].append({'attributeID': 334, 'attributeName': 'Big Goons'})
        self.dh.data['dgmtypeeffects'].append({'typeID': 556, 'effectID': 111})
        self.dh.data['dgmeffects'].append({'effectID': 111, 'preExpression': 34, 'postExpression': 34})
        self.dh.data['dgmexpressions'].append({
            'expressionID': 34, 'operandID': Operand.def_attr, 'arg1': 2357,
            'arg2': 66, 'expressionValue': 'BigGoons', 'expressionTypeID': 567,
            'expressionGroupID': 322, 'expressionAttributeID': None
        })
        mod_builder.return_value.build.return_value = ([], 0)
        self.run_generator()
        self.assertEqual(len(self.log), 2)
        literal_stats = self.log[0]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        self.assertEqual(
            literal_stats.msg, 'conversion of literal references to IDs in dgmexpressions: 1 successful, 0 failed')
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        expressions = mod_builder.mock_calls[0][1][0]
        self.assertEqual(len(expressions), 1)
        expected = {
            'expressionID': 34, 'operandID': Operand.def_attr, 'arg1': 2357, 'arg2': 66,
            'expressionValue': None, 'expressionTypeID': 567, 'expressionGroupID': 322,
            'expressionAttributeID': 334, 'table_pos': 0
        }
        self.assertIn(expected, expressions)

    def test_unstripped(self, mod_builder):
        self.dh.data['evetypes'].append({'typeID': 556, 'groupID': 1, 'typeName_en-us': 'Big Gun 3'})
        self.dh.data['dgmtypeeffects'].append({'typeID': 556, 'effectID': 111})
        self.dh.data['dgmeffects'].append({'effectID': 111, 'preExpression': 57, 'postExpression': 57})
        self.dh.data['dgmexpressions'].append({
            'expressionID': 57, 'operandID': Operand.def_type, 'arg1': 5007,
            'arg2': 66, 'expressionValue': 'Big Gun 3', 'expressionTypeID': None,
            'expressionGroupID': 567, 'expressionAttributeID': 102
        })
        mod_builder.return_value.build.return_value = ([], 0)
        self.run_generator()
        self.assertEqual(len(self.log), 2)
        literal_stats = self.log[0]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        self.assertEqual(
            literal_stats.msg, 'conversion of literal references to IDs in dgmexpressions: 1 successful, 0 failed')
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        expressions = mod_builder.mock_calls[0][1][0]
        self.assertEqual(len(expressions), 1)
        expected = {
            'expressionID': 57, 'operandID': Operand.def_type, 'arg1': 5007, 'arg2': 66,
            'expressionValue': None, 'expressionTypeID': 556, 'expressionGroupID': 567,
            'expressionAttributeID': 102, 'table_pos': 0
        }
        self.assertIn(expected, expressions)

    def test_multiple_warning(self, mod_builder):
        self.dh.data['evetypes'].append({'typeID': 556, 'groupID': 1, 'typeName_en-us': 'Big Gun 3'})
        self.dh.data['evetypes'].append({'typeID': 35, 'groupID': 1, 'typeName_en-us': '     BigGun 3  '})
        # Using this name, we'll also check that already 'stripped' name (without space
        # symbols) does not add carrier's ID multiple times anywhere, including warning
        self.dh.data['evetypes'].append({'typeID': 22, 'groupID': 1, 'typeName_en-us': 'BigGun3'})
        self.dh.data['dgmtypeeffects'].append({'typeID': 556, 'effectID': 111})
        self.dh.data['dgmtypeeffects'].append({'typeID': 35, 'effectID': 11})
        self.dh.data['dgmeffects'].append({'effectID': 111, 'preExpression': 57, 'postExpression': 57})
        self.dh.data['dgmeffects'].append({'effectID': 11, 'preExpression': 589, 'postExpression': 589})
        self.dh.data['dgmexpressions'].append({
            'expressionID': 57, 'operandID': Operand.def_type, 'arg1': 5007,
            'arg2': 66, 'expressionValue': 'BigGun3', 'expressionTypeID': None,
            'expressionGroupID': 567, 'expressionAttributeID': 102
        })
        self.dh.data['dgmexpressions'].append({
            'expressionID': 589, 'operandID': Operand.def_type, 'arg1': 507,
            'arg2': 6, 'expressionValue': 'BigGun3', 'expressionTypeID': None,
            'expressionGroupID': 57, 'expressionAttributeID': 12
        })
        mod_builder.return_value.build.return_value = ([], 0)
        self.run_generator()
        self.assertEqual(len(self.log), 3)
        multiple_warning = self.log[0]
        self.assertEqual(multiple_warning.name, 'eos.data.cache_generator.converter')
        self.assertEqual(multiple_warning.levelno, logging.WARNING)
        self.assertEqual(
            multiple_warning.msg,
            'multiple typeIDs found for symbolic name "BigGun3": (556, 35, 22), using 556'
        )
        literal_stats = self.log[1]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        self.assertEqual(
            literal_stats.msg, 'conversion of literal references to IDs in dgmexpressions: 2 successful, 0 failed')
        clean_stats = self.log[2]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        expressions = mod_builder.mock_calls[0][1][0]
        self.assertEqual(len(expressions), 2)
        expected = {
            'expressionID': 57, 'operandID': Operand.def_type, 'arg1': 5007, 'arg2': 66,
            'expressionValue': None, 'expressionTypeID': 556, 'expressionGroupID': 567,
            'expressionAttributeID': 102, 'table_pos': 0
        }
        self.assertIn(expected, expressions)
        expected = {
            'expressionID': 589, 'operandID': Operand.def_type, 'arg1': 507, 'arg2': 6,
            'expressionValue': None, 'expressionTypeID': 556, 'expressionGroupID': 57,
            'expressionAttributeID': 12, 'table_pos': 1
        }
        self.assertIn(expected, expressions)

    def test_failed_conversion(self, mod_builder):
        self.dh.data['evetypes'].append({'typeID': 556, 'groupID': 1, 'typeName_en-us': 'Big Gun 4'})
        self.dh.data['dgmtypeeffects'].append({'typeID': 556, 'effectID': 111})
        self.dh.data['dgmeffects'].append({'effectID': 111, 'preExpression': 57, 'postExpression': 57})
        self.dh.data['dgmexpressions'].append({
            'expressionID': 57, 'operandID': Operand.def_type, 'arg1': 5007,
            'arg2': 66, 'expressionValue': 'BigGun3', 'expressionTypeID': None,
            'expressionGroupID': 567, 'expressionAttributeID': 102
        })
        mod_builder.return_value.build.return_value = ([], 0)
        self.run_generator()
        self.assertEqual(len(self.log), 2)
        literal_stats = self.log[0]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        self.assertEqual(
            literal_stats.msg, 'conversion of literal references to IDs in dgmexpressions: 0 successful, 1 failed')
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        # As in expression conversion, we're verifying expressions
        # passed to modifier builder, as it's much easier to do
        expressions = mod_builder.mock_calls[0][1][0]
        self.assertEqual(len(expressions), 1)
        expected = {
            'expressionID': 57, 'operandID': Operand.def_type, 'arg1': 5007, 'arg2': 66,
            'expressionValue': 'BigGun3', 'expressionTypeID': None, 'expressionGroupID': 567,
            'expressionAttributeID': 102, 'table_pos': 0
        }
        self.assertIn(expected, expressions)
