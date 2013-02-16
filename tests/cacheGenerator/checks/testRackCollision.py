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


class TestRackCollision(GeneratorTestCase):
    """
    Make sure that rack collision is detected,
    and it is detected after cleanup.
    """

    def setUp(self):
        GeneratorTestCase.setUp(self)
        self.item = {'typeID': 1, 'groupID': 1}
        self.dh.data['invtypes'].append(self.item)
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 13})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 11})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 12})
        self.dh.data['dgmeffects'].append({'effectID': 11})
        self.dh.data['dgmeffects'].append({'effectID': 12})
        self.dh.data['dgmeffects'].append({'effectID': 13})

    def testCollision(self):
        data = self.runGenerator()
        self.assertEqual(len(self.log), 2)
        cleanStats = self.log[0]
        self.assertEqual(cleanStats.name, 'eos_test.cacheGenerator')
        self.assertEqual(cleanStats.levelno, Logger.INFO)
        logRecord = self.log[1]
        self.assertEqual(logRecord.name, 'eos_test.cacheGenerator')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, '2 rows contain colliding module racks, removing them')
        self.assertEqual(len(data['types']), 1)
        self.assertIn(1, data['types'])
        typeEffects = data['types'][1]['effects']
        self.assertEqual(len(typeEffects), 1)
        self.assertIn(13, typeEffects)
        self.assertEqual(len(data['effects']), 3)

    def testCleaned(self):
        del self.item['groupID']
        data = self.runGenerator()
        self.assertEqual(len(self.log), 1)
        cleanStats = self.log[0]
        self.assertEqual(cleanStats.name, 'eos_test.cacheGenerator')
        self.assertEqual(cleanStats.levelno, Logger.INFO)
        self.assertEqual(len(data['types']), 0)
        self.assertEqual(len(data['effects']), 0)
