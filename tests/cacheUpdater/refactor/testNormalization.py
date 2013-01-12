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


from eos.eve.const import Attribute
from eos.tests.cacheUpdater.updaterTestCase import UpdaterTestCase
from eos.tests.environment import Logger


class TestNormalization(UpdaterTestCase):
    """Check that all normalization jobs function as expected"""

    def testBasicAttrRadius(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1, 'radius': 50.0})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 1)
        cleanStats = self.log[0]
        self.assertEqual(cleanStats.name, 'eos_test.cacheUpdater')
        self.assertEqual(cleanStats.levelno, Logger.INFO)
        self.assertIn((Attribute.radius, 50.0), data['types'][1][9])

    def testBasicAttrMass(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1, 'mass': 5.0})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 1)
        cleanStats = self.log[0]
        self.assertEqual(cleanStats.name, 'eos_test.cacheUpdater')
        self.assertEqual(cleanStats.levelno, Logger.INFO)
        self.assertIn((Attribute.mass, 5.0), data['types'][1][9])

    def testBasicAttrVolume(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1, 'volume': 500.0})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 1)
        cleanStats = self.log[0]
        self.assertEqual(cleanStats.name, 'eos_test.cacheUpdater')
        self.assertEqual(cleanStats.levelno, Logger.INFO)
        self.assertIn((Attribute.volume, 500.0), data['types'][1][9])

    def testBasicAttrCapacity(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1, 'capacity': 0.5})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 1)
        cleanStats = self.log[0]
        self.assertEqual(cleanStats.name, 'eos_test.cacheUpdater')
        self.assertEqual(cleanStats.levelno, Logger.INFO)
        self.assertIn((Attribute.capacity, 0.5), data['types'][1][9])
