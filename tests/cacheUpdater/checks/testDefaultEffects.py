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


class TestDefaultEffects(UpdaterTestCase):
    """
    Check that filtering out superfluous default effects
    occurs after data filtering, and that it occurs at all.
    """

    def setUp(self):
        UpdaterTestCase.setUp(self)
        self.item = {'typeID': 1, 'groupID': 1}
        self.dh.data['invtypes'].append(self.item)
        self.effLink1 = {'typeID': 1, 'effectID': 1}
        self.effLink2 = {'typeID': 1, 'effectID': 2}
        self.dh.data['dgmtypeeffects'].append(self.effLink1)
        self.dh.data['dgmtypeeffects'].append(self.effLink2)
        self.dh.data['dgmeffects'].append({'effectID': 1, 'falloffAttributeID': 10})
        self.dh.data['dgmeffects'].append({'effectID': 2, 'falloffAttributeID': 20})

    def testNormal(self):
        self.effLink1['isDefault'] = False
        self.effLink2['isDefault'] = True
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 1)
        cleanStats = self.log[0]
        self.assertEqual(cleanStats.name, 'eos_test.cacheUpdater')
        self.assertEqual(cleanStats.levelno, Logger.INFO)
        self.assertEqual(len(data['types']), 1)
        self.assertIn(1, data['types'])
        self.assertEqual(data['types'][1][5], 20)

    def testDuplicate(self):
        self.effLink1['isDefault'] = True
        self.effLink2['isDefault'] = True
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 2)
        cleanStats = self.log[0]
        self.assertEqual(cleanStats.name, 'eos_test.cacheUpdater')
        self.assertEqual(cleanStats.levelno, Logger.INFO)
        logRecord = self.log[1]
        self.assertEqual(logRecord.name, 'eos_test.cacheUpdater')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, 'data contains 1 excessive default effects, marking them as non-default')
        self.assertEqual(len(data['types']), 1)
        self.assertIn(1, data['types'])
        self.assertEqual(data['types'][1][5], 10)
        # Make sure effects are not removed
        self.assertEqual(len(data['effects']), 2)
        self.assertIn(1, data['effects'])
        self.assertIn(2, data['effects'])

    def testCleanup(self):
        del self.item['groupID']
        self.effLink1['isDefault'] = True
        self.effLink2['isDefault'] = True
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 1)
        cleanStats = self.log[0]
        self.assertEqual(cleanStats.name, 'eos_test.cacheUpdater')
        self.assertEqual(cleanStats.levelno, Logger.INFO)
        self.assertEqual(len(data['types']), 0)
        self.assertEqual(len(data['effects']), 0)
