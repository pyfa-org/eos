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

from eos.tests.cacheGenerator.generatorTestCase import GeneratorTestCase
from eos.tests.environment import Logger


class TestConversionExpression(GeneratorTestCase):
    """
    Appropriate data should be saved into appropriate
    indexes of object representing expression.
    """

    @patch('eos.data.cacheGenerator.converter.ModifierBuilder')
    def testFields(self, modBuilder):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 111})
        self.dh.data['dgmeffects'].append({'effectID': 111, 'preExpression': 57, 'postExpression': 41})
        self.dh.data['dgmexpressions'].append({'expressionTypeID': 502, 'expressionValue': None, 'randomField': 'vals',
                                               'operandID': 6, 'arg1': 1009, 'expressionID': 41, 'arg2': 15,
                                               'expressionAttributeID': 90, 'expressionGroupID': 451})
        self.dh.data['dgmexpressions'].append({'expressionGroupID': 567, 'arg2': 66, 'operandID': 33, 'arg1': 5007,
                                               'expressionID': 57, 'expressionTypeID': 551, 'randoom': True,
                                               'expressionAttributeID': 102, 'expressionValue': 'Kurr'})
        modBuilder.return_value.buildEffect.return_value = ([], 0)
        self.runGenerator()
        self.assertEqual(len(self.log), 1)
        cleanStats = self.log[0]
        self.assertEqual(cleanStats.name, 'eos_test.cacheGenerator')
        self.assertEqual(cleanStats.levelno, Logger.INFO)
        # As expressions are absent in final container,
        # check those which were passed to modifier builder
        expressions = modBuilder.mock_calls[0][1][0]
        self.assertEqual(len(expressions), 2)
        # It's fine that additional fields get into final expression set,
        # because they will be replaced by modifiers anyway
        expected = {'expressionID': 41, 'operandID': 6, 'arg1': 1009, 'arg2': 15, 'expressionValue': None,
                    'expressionTypeID': 502, 'expressionGroupID': 451, 'expressionAttributeID': 90,
                    'tablePos': 0, 'randomField': 'vals'}
        self.assertIn(expected, expressions)
        expected = {'expressionID': 57, 'operandID': 33, 'arg1': 5007, 'arg2': 66, 'expressionValue': 'Kurr',
                    'expressionTypeID': 551, 'expressionGroupID': 567, 'expressionAttributeID': 102,
                    'tablePos': 1, 'randoom': True}
        self.assertIn(expected, expressions)
