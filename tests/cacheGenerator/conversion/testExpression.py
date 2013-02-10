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


from eos.tests.cacheGenerator.generatorTestCase import GeneratorTestCase
from eos.tests.environment import Logger


class TestConversionExpression(GeneratorTestCase):
    """
    Expressions generated out of passed data are consumed
    mid-process to generate modifiers, so we use our fake
    modifier builder, defined in environment, to check that
    expressions passed to it are correct.
    """

    def testFields(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 111})
        self.dh.data['dgmeffects'].append({'effectID': 111, 'preExpression': 700, 'postExpression': 800})
        self.dh.data['dgmexpressions'].append({'expressionTypeID': 502, 'expressionValue': None, 'randomField': 'vals',
                                               'operandID': 6, 'arg1': 1009, 'expressionID': 800, 'arg2': 15,
                                               'expressionAttributeID': 90, 'expressionGroupID': 451})
        self.dh.data['dgmexpressions'].append({'expressionGroupID': 567, 'arg2': 66, 'operandID': 33, 'arg1': 5007,
                                               'expressionID': 700, 'expressionTypeID': 551, 'randoom': True,
                                               'expressionAttributeID': 102, 'expressionValue': 'Kurr'})
        data = self.runGenerator()
        self.assertEqual(len(self.log), 1)
        cleanStats = self.log[0]
        self.assertEqual(cleanStats.name, 'eos_test.cacheGenerator')
        self.assertEqual(cleanStats.levelno, Logger.INFO)
        # Check custom build status returned by modifier builder,
        # which says us if passed expressions were fine or not
        self.assertIn(111, data['effects'])
        effectRow = data['effects'][111]
        self.assertEqual(effectRow['buildStatus'], 8000)
