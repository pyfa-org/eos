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


class TestConversionEffect(GeneratorTestCase):
    """
    Appropriate data should be saved into appropriate
    indexes of object representing effect.
    """

    def testFields(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 111})
        self.dh.data['dgmeffects'].append({'postExpression': 979, 'effectID': 111, 'isOffensive': True, 'effectCategory': 8,
                                           'isAssistance': False, 'fittingUsageChanceAttributeID': 96, 'preExpression': 24,
                                           'durationAttributeID': 781, 'randomField': 666})
        data = self.gen.run(self.dh)
        self.assertEqual(len(self.log), 1)
        cleanStats = self.log[0]
        self.assertEqual(cleanStats.name, 'eos_test.cacheGenerator')
        self.assertEqual(cleanStats.levelno, Logger.INFO)
        self.assertEqual(len(data['effects']), 1)
        self.assertIn(111, data['effects'])
        effectRow = data['effects'][111]
        self.assertEqual(effectRow['effectCategory'], 8)
        self.assertEqual(effectRow['isOffensive'], True)
        self.assertEqual(effectRow['isAssistance'], False)
        self.assertEqual(effectRow['fittingUsageChanceAttributeId'], 96)
        self.assertEqual(effectRow['preExpressionId'], 24)
        self.assertEqual(effectRow['postExpressionId'], 979)
