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


from eos.data.cacheGenerator import CacheGenerator
from eos.data.cacheObjects import Modifier
from eos.tests.environment import Logger
from eos.tests.eosTestCase import EosTestCase
from .environment import DataHandler


class GeneratorTestCase(EosTestCase):

    def setUp(self):
        EosTestCase.setUp(self)
        self.dh = DataHandler()

    def runGenerator(self):
        """
        Run generator and rework data structure into
        keyed tables so it's easier to check.
        """
        generator = CacheGenerator(Logger())
        data = generator.run(self.dh)
        keys = {'types': 'typeId',
                'attributes': 'attributeId',
                'effects': 'effectId',
                'expressions': 'expressionId',
                'modifiers': 'modifierId'}
        keyedData = {}
        for tableName in data:
            keyedTable = {}
            keyName = keys[tableName]
            for row in data[tableName]:
                key = row[keyName]
                keyedTable[key] = row
            keyedData[tableName] = keyedTable
        return keyedData

    def mod(self, *args, **kwargs):
        """Instantiate and return modifier."""
        return Modifier(*args, **kwargs)
