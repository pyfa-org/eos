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


from eos.tests.cacheUpdater.updaterTestCase import UpdaterTestCase
from eos.tests.environment import Logger


class TestConversionType(UpdaterTestCase):
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
                                           'fittingUsageChanceAttributeID': 96, 'preExpression': 24, 'postExpression': 979,
                                           'durationAttributeID': 78, 'dischargeAttributeID': 72, 'rangeAttributeID': 2,
                                           'falloffAttributeID': 3, 'trackingSpeedAttributeID': 6})
        self.dh.data['dgmeffects'].append({'effectID': 1111, 'effectCategory': 85, 'isOffensive': False, 'isAssistance': True,
                                           'fittingUsageChanceAttributeID': 41, 'preExpression': 79, 'postExpression': 5,
                                           'durationAttributeID': 781, 'dischargeAttributeID': 752, 'rangeAttributeID': 26,
                                           'falloffAttributeID': 33, 'trackingSpeedAttributeID': 68})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 1)
        cleanStats = self.log[0]
        self.assertEqual(cleanStats.name, 'eos_test.cacheUpdater')
        self.assertEqual(cleanStats.levelno, Logger.INFO)
        self.assertEqual(len(data['types']), 1)
        self.assertIn(1, data['types'])
        item = data['types'][1]
        self.assertEqual(len(item), 10)
        self.assertEqual(item[0], 6)
        self.assertEqual(item[1], 16)
        self.assertEqual(item[2], 78)
        self.assertEqual(item[3], 72)
        self.assertEqual(item[4], 2)
        self.assertEqual(item[5], 3)
        self.assertEqual(item[6], 6)
        self.assertIs(item[7], True)
        self.assertEqual(len(item[8]), 2)
        self.assertIn(111, item[8])
        self.assertIn(1111, item[8])
        self.assertEqual(len(item[9]), 2)
        self.assertIn((5, 10.0), item[9])
        self.assertIn((80, 180.0), item[9])
