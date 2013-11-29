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

from eos.const.eve import Operand
from eos.tests.cache_generator.generator_testcase import GeneratorTestCase
from eos.tests.environment import Logger


@patch('eos.data.cache_generator.converter.ModifierBuilder')
class TestNormalizationIdzing(GeneratorTestCase):
    """Check that conversion of symbolic references to IDs functions."""

    def test_type_idzing(self, mod_builder):
        self.dh.data['invtypes'].append({'typeID': 556, 'groupID': 1, 'typeName': 'Big Gun 3'})
        self.dh.data['dgmtypeeffects'].append({'typeID': 556, 'effectID': 111})
        self.dh.data['dgmeffects'].append({'effectID': 111, 'preExpression': 57, 'postExpression': 57})
        self.dh.data['dgmexpressions'].append({'expressionID': 57, 'operandID': Operand.def_type, 'arg1': 5007,
                                               'arg2': 66, 'expressionValue': 'BigGun3', 'expressionTypeID': None,
                                               'expressionGroupID': 567, 'expressionAttributeID': 102})
        mod_builder.return_value.build_effect.return_value = ([], 0)
        self.run_generator()
        self.assertEqual(len(self.log), 1)
        clean_stats = self.log[0]
        self.assertEqual(clean_stats.name, 'eos_test.cache_generator')
        self.assertEqual(clean_stats.levelno, Logger.INFO)
        # As in expression conversion, we're verifying expressions
        # passed to modifier builder, as it's much easier to do
        expressions = mod_builder.mock_calls[0][1][0]
        self.assertEqual(len(expressions), 1)
        expected = {'expressionID': 57, 'operandID': Operand.def_type, 'arg1': 5007, 'arg2': 66,
                    'expressionValue': None, 'expressionTypeID': 556, 'expressionGroupID': 567,
                    'expressionAttributeID': 102, 'table_pos': 0}
        self.assertIn(expected, expressions)

    def test_group_idzing(self, mod_builder):
        self.dh.data['invtypes'].append({'typeID': 556, 'groupID': 668, 'typeName': ''})
        self.dh.data['invgroups'].append({'groupID': 668, 'categoryID': 16, 'groupName': 'Big Guns'})
        self.dh.data['dgmtypeeffects'].append({'typeID': 556, 'effectID': 111})
        self.dh.data['dgmeffects'].append({'effectID': 111, 'preExpression': 57, 'postExpression': 57})
        self.dh.data['dgmexpressions'].append({'expressionID': 57, 'operandID': Operand.def_grp, 'arg1': 5007,
                                               'arg2': 66, 'expressionValue': 'BigGuns', 'expressionTypeID': 567,
                                               'expressionGroupID': None, 'expressionAttributeID': 102})
        mod_builder.return_value.build_effect.return_value = ([], 0)
        self.run_generator()
        self.assertEqual(len(self.log), 1)
        clean_stats = self.log[0]
        self.assertEqual(clean_stats.name, 'eos_test.cache_generator')
        self.assertEqual(clean_stats.levelno, Logger.INFO)
        # As in expression conversion, we're verifying expressions
        # passed to modifier builder, as it's much easier to do
        expressions = mod_builder.mock_calls[0][1][0]
        self.assertEqual(len(expressions), 1)
        expected = {'expressionID': 57, 'operandID': Operand.def_grp, 'arg1': 5007, 'arg2': 66,
                    'expressionValue': None, 'expressionTypeID': 567, 'expressionGroupID': 668,
                    'expressionAttributeID': 102, 'table_pos': 0}
        self.assertIn(expected, expressions)

    def test_attribute_idzing(self, mod_builder):
        self.dh.data['invtypes'].append({'typeID': 556, 'groupID': 668, 'typeName': ''})
        self.dh.data['invgroups'].append({'groupID': 668, 'categoryID': 16, 'groupName': 'Big Guns'})
        self.dh.data['dgmtypeeffects'].append({'typeID': 556, 'effectID': 111})
        self.dh.data['dgmeffects'].append({'effectID': 111, 'preExpression': 57, 'postExpression': 57})
        self.dh.data['dgmexpressions'].append({'expressionID': 57, 'operandID': Operand.def_grp, 'arg1': 5007,
                                               'arg2': 66, 'expressionValue': 'BigGuns', 'expressionTypeID': 567,
                                               'expressionGroupID': None, 'expressionAttributeID': 102})
        mod_builder.return_value.build_effect.return_value = ([], 0)
        self.run_generator()
        self.assertEqual(len(self.log), 1)
        clean_stats = self.log[0]
        self.assertEqual(clean_stats.name, 'eos_test.cache_generator')
        self.assertEqual(clean_stats.levelno, Logger.INFO)
        # As in expression conversion, we're verifying expressions
        # passed to modifier builder, as it's much easier to do
        expressions = mod_builder.mock_calls[0][1][0]
        self.assertEqual(len(expressions), 1)
        expected = {'expressionID': 57, 'operandID': Operand.def_grp, 'arg1': 5007, 'arg2': 66,
                    'expressionValue': None, 'expressionTypeID': 567, 'expressionGroupID': 668,
                    'expressionAttributeID': 102, 'table_pos': 0}
        self.assertIn(expected, expressions)

    def test_unstripped(self, mod_builder):
        self.dh.data['invtypes'].append({'typeID': 556, 'groupID': 1, 'typeName': 'Big Gun 3'})
        self.dh.data['dgmtypeeffects'].append({'typeID': 556, 'effectID': 111})
        self.dh.data['dgmeffects'].append({'effectID': 111, 'preExpression': 57, 'postExpression': 57})
        self.dh.data['dgmexpressions'].append({'expressionID': 57, 'operandID': Operand.def_type, 'arg1': 5007,
                                               'arg2': 66, 'expressionValue': 'Big Gun 3', 'expressionTypeID': None,
                                               'expressionGroupID': 567, 'expressionAttributeID': 102})
        mod_builder.return_value.build_effect.return_value = ([], 0)
        self.run_generator()
        self.assertEqual(len(self.log), 1)
        clean_stats = self.log[0]
        self.assertEqual(clean_stats.name, 'eos_test.cache_generator')
        self.assertEqual(clean_stats.levelno, Logger.INFO)
        # As in expression conversion, we're verifying expressions
        # passed to modifier builder, as it's much easier to do
        expressions = mod_builder.mock_calls[0][1][0]
        self.assertEqual(len(expressions), 1)
        expected = {'expressionID': 57, 'operandID': Operand.def_type, 'arg1': 5007, 'arg2': 66,
                    'expressionValue': None, 'expressionTypeID': 556, 'expressionGroupID': 567,
                    'expressionAttributeID': 102, 'table_pos': 0}
        self.assertIn(expected, expressions)

    def test_multiple_warning(self, mod_builder):
        self.dh.data['invtypes'].append({'typeID': 556, 'groupID': 1, 'typeName': 'Big Gun 3'})
        self.dh.data['invtypes'].append({'typeID': 35, 'groupID': 1, 'typeName': '     BigGun 3  '})
        # Using this name, we'll also check that already 'stripped' name (without space
        # symbols) does not add carrier's ID multiple times anywhere, including warning
        self.dh.data['invtypes'].append({'typeID': 22, 'groupID': 1, 'typeName': 'BigGun3'})
        self.dh.data['dgmtypeeffects'].append({'typeID': 556, 'effectID': 111})
        self.dh.data['dgmeffects'].append({'effectID': 111, 'preExpression': 57, 'postExpression': 57})
        self.dh.data['dgmexpressions'].append({'expressionID': 57, 'operandID': Operand.def_type, 'arg1': 5007,
                                               'arg2': 66, 'expressionValue': 'BigGun3', 'expressionTypeID': None,
                                               'expressionGroupID': 567, 'expressionAttributeID': 102})
        mod_builder.return_value.build_effect.return_value = ([], 0)
        self.run_generator()
        self.assertEqual(len(self.log), 2)
        multiple_warning = self.log[0]
        self.assertEqual(multiple_warning.name, 'eos_test.cache_generator')
        self.assertEqual(multiple_warning.levelno, Logger.WARNING)
        self.assertEqual(multiple_warning.msg,
                         'multiple typeIDs found for symbolic name BigGun3: (556, 35, 22), using 556')
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos_test.cache_generator')
        self.assertEqual(clean_stats.levelno, Logger.INFO)
        # As in expression conversion, we're verifying expressions
        # passed to modifier builder, as it's much easier to do
        expressions = mod_builder.mock_calls[0][1][0]
        self.assertEqual(len(expressions), 1)
        expected = {'expressionID': 57, 'operandID': Operand.def_type, 'arg1': 5007, 'arg2': 66,
                    'expressionValue': None, 'expressionTypeID': 556, 'expressionGroupID': 567,
                    'expressionAttributeID': 102, 'table_pos': 0}
        self.assertIn(expected, expressions)
