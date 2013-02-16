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


class TestConversionType(GeneratorTestCase):
    """
    Appropriate data should be saved into appropriate
    indexes of object representing effect.
    """

    def testFields(self):
        self.dh.data['invtypes'].append({'randomField': 66, 'typeID': 1, 'groupID': 6})
        self.dh.data['invgroups'].append({'categoryID': 16, 'fittableNonSingleton': True, 'groupID': 6})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 5, 'value': 10.0})
        self.dh.data['dgmtypeattribs'].append({'attributeID': 80, 'typeID': 1, 'value': 180.0})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 111, 'isDefault': True})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 1111, 'isDefault': False})
        self.dh.data['dgmeffects'].append({'effectID': 111, 'effectCategory': 8, 'isOffensive': True, 'isAssistance': False,
                                           'fittingUsageChanceAttributeID': 96, 'preExpression': None, 'postExpression': None,
                                           'durationAttributeID': 78, 'dischargeAttributeID': 72, 'rangeAttributeID': 2,
                                           'falloffAttributeID': 3, 'trackingSpeedAttributeID': 6})
        self.dh.data['dgmeffects'].append({'effectID': 1111, 'effectCategory': 85, 'isOffensive': False, 'isAssistance': True,
                                           'fittingUsageChanceAttributeID': 41, 'preExpression': None, 'postExpression': None,
                                           'durationAttributeID': 781, 'dischargeAttributeID': 752, 'rangeAttributeID': 26,
                                           'falloffAttributeID': 33, 'trackingSpeedAttributeID': 68})
        data = self.runGenerator()
        self.assertEqual(len(self.log), 1)
        cleanStats = self.log[0]
        self.assertEqual(cleanStats.name, 'eos_test.cacheGenerator')
        self.assertEqual(cleanStats.levelno, Logger.INFO)
        self.assertEqual(len(data['types']), 1)
        self.assertIn(1, data['types'])
        typeRow = data['types'][1]
        self.assertEqual(len(typeRow), 11)
        self.assertEqual(typeRow['groupId'], 6)
        self.assertEqual(typeRow['categoryId'], 16)
        self.assertEqual(typeRow['durationAttributeId'], 78)
        self.assertEqual(typeRow['dischargeAttributeId'], 72)
        self.assertEqual(typeRow['rangeAttributeId'], 2)
        self.assertEqual(typeRow['falloffAttributeId'], 3)
        self.assertEqual(typeRow['trackingSpeedAttributeId'], 6)
        self.assertIs(typeRow['fittableNonSingleton'], True)
        typeEffects = typeRow['effects']
        self.assertEqual(len(typeEffects), 2)
        self.assertIn(111, typeEffects)
        self.assertIn(1111, typeEffects)
        typeAttributes = typeRow['attributes']
        self.assertEqual(len(typeAttributes), 2)
        self.assertEqual(typeAttributes[5], 10.0)
        self.assertEqual(typeAttributes[80], 180.0)
