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


class TestRackCollision(UpdaterTestCase):
    """
    Make sure that rack collision is detected,
    and it is detected after cleanup.
    """

    def testCollision(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 13})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 11})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 12})
        self.dh.data['dgmeffects'].append({'effectID': 11, 'preExpression': 50})
        self.dh.data['dgmeffects'].append({'effectID': 12, 'preExpression': 55})
        self.dh.data['dgmeffects'].append({'effectID': 13, 'preExpression': 555})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 2)
        cleanStats = self.log[0]
        self.assertEqual(cleanStats.name, 'eos_test.cacheUpdater')
        self.assertEqual(cleanStats.levelno, Logger.INFO)
        logRecord = self.log[1]
        self.assertEqual(logRecord.name, 'eos_test.cacheUpdater')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, '2 rows contain colliding module racks, removing them')
        self.assertEqual(len(data['types']), 1)
        self.assertIn(1, data['types'])
        self.assertEqual(data['types'][1][8], (13,))
        self.assertEqual(len(data['effects']), 3)

    def testCleaned(self):
        self.dh.data['invtypes'].append({'typeID': 1})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 13})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 11})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 12})
        self.dh.data['dgmeffects'].append({'effectID': 11, 'preExpression': 50})
        self.dh.data['dgmeffects'].append({'effectID': 12, 'preExpression': 55})
        self.dh.data['dgmeffects'].append({'effectID': 13, 'preExpression': 555})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 1)
        cleanStats = self.log[0]
        self.assertEqual(cleanStats.name, 'eos_test.cacheUpdater')
        self.assertEqual(cleanStats.levelno, Logger.INFO)
        self.assertEqual(len(data['types']), 0)
        self.assertEqual(len(data['effects']), 0)
