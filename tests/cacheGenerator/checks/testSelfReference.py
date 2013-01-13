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


class TestSelfReference(GeneratorTestCase):
    """
    Some of type IDs are reserved by engine, source data
    is not allowed to have types with such typeID.
    """

    def testTypeId(self):
        self.dh.data['invtypes'].append({'typeID': -1, 'groupID': 1})
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1})
        data = self.gen.run(self.dh)
        self.assertEqual(len(self.log), 2)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.cacheGenerator')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, 'type self-reference (ID -1) exists, removing type')
        cleanStats = self.log[1]
        self.assertEqual(cleanStats.name, 'eos_test.cacheGenerator')
        self.assertEqual(cleanStats.levelno, Logger.INFO)
        self.assertEqual(len(data['types']), 1)
        self.assertIn(1, data['types'])

    def testCleaned(self):
        # Make sure check is ran before cleanup
        self.dh.data['invtypes'].append({'typeID': -1})
        self.dh.data['invtypes'].append({'typeID': 1})
        data = self.gen.run(self.dh)
        self.assertEqual(len(self.log), 2)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.cacheGenerator')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, 'type self-reference (ID -1) exists, removing type')
        cleanStats = self.log[1]
        self.assertEqual(cleanStats.name, 'eos_test.cacheGenerator')
        self.assertEqual(cleanStats.levelno, Logger.INFO)
        self.assertEqual(len(data['types']), 0)
