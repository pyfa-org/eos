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


class TestPrimaryKey(UpdaterTestCase):
    """Check that only valid primary keys pass checks"""

    def testSingleProperPk(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1})
        self.dh.data['invtypes'].append({'typeID': 2, 'groupID': 1})
        data = self.updater.run(self.dh)
        self.assertIn(1, data['types'])
        self.assertIn(2, data['types'])

    def testSingleNoPk(self):
        self.dh.data['invtypes'].append({'groupID': 1})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.cacheUpdater')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, '1 rows in table invtypes have invalid PKs, removing them')
        self.assertEqual(len(data['types']), 0)

    def testSingleInvalid(self):
        self.dh.data['invtypes'].append({'typeID': 1.5, 'groupID': 1})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.cacheUpdater')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, '1 rows in table invtypes have invalid PKs, removing them')
        self.assertEqual(len(data['types']), 0)

    def testSingleDuplicate(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1})
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 920})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.cacheUpdater')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, '1 rows in table invtypes have invalid PKs, removing them')
        self.assertEqual(len(data['types']), 1)
        self.assertEqual(data['types'][1][0], 1)

    def testSingleDuplicateReverse(self):
        # Make sure first fed by dataHandler row is accepted
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 920})
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.cacheUpdater')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, '1 rows in table invtypes have invalid PKs, removing them')
        self.assertEqual(len(data['types']), 1)
        self.assertEqual(data['types'][1][0], 920)

    def testSingleCleaned(self):
        # Make sure check is ran before cleanup
        self.dh.data['invtypes'].append({'typeID': 1})
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 920})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.cacheUpdater')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, '1 rows in table invtypes have invalid PKs, removing them')
        self.assertEqual(len(data['types']), 0)

    def testDualProperPk(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 100, 'value': 50.0})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 50, 'value': 100.0})
        data = self.updater.run(self.dh)
        self.assertIn((100, 50.0), data['types'][1][9])
        self.assertIn((50, 100.0), data['types'][1][9])

    def testDualNoPk(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'value': 50.0})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.cacheUpdater')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, '1 rows in table dgmtypeattribs have invalid PKs, removing them')
        self.assertEqual(len(data['types'][1][9]), 0)

    def testDualInvalid(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 100.1, 'value': 50.0})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.cacheUpdater')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, '1 rows in table dgmtypeattribs have invalid PKs, removing them')
        self.assertEqual(len(data['types'][1][9]), 0)

    def testDualDuplicate(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 100, 'value': 50.0})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 100, 'value': 5.0})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.cacheUpdater')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, '1 rows in table dgmtypeattribs have invalid PKs, removing them')
        self.assertEqual(len(data['types'][1][9]), 1)
        self.assertIn((100, 50.0), data['types'][1][9])

    def testDualCleaned(self):
        # Make sure check is ran before cleanup
        self.dh.data['invtypes'].append({'typeID': 1})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 100, 'value': 50.0})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 100, 'value': 5.0})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.cacheUpdater')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, '1 rows in table dgmtypeattribs have invalid PKs, removing them')
        self.assertEqual(len(data['types']), 0)

    def testDualDuplicateReverse(self):
        # Make sure first fed by dataHandler row is accepted
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 100, 'value': 5.0})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 100, 'value': 50.0})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.cacheUpdater')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, '1 rows in table dgmtypeattribs have invalid PKs, removing them')
        self.assertEqual(len(data['types'][1][9]), 1)
        self.assertIn((100, 5.0), data['types'][1][9])

    # Now, when PK-related checks cover invtypes (single PK)
    # and dgmtypeattribs (dual PK) tables, run simple tests on
    # the rest of the tables to make sure they are covered
    def testInvgroups(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1})
        self.dh.data['invgroups'].append({'groupID': 1, 'categoryID': 7})
        self.dh.data['invgroups'].append({'groupID': 1, 'categoryID': 32})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.cacheUpdater')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, '1 rows in table invgroups have invalid PKs, removing them')
        self.assertEqual(len(data['types']), 1)
        self.assertEqual(data['types'][1][1], 7)

    def testDgmattribs(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 7, 'value': 8.0})
        self.dh.data['dgmattribs'].append({'attributeID': 7, 'maxAttributeID': 50})
        self.dh.data['dgmattribs'].append({'attributeID': 7, 'maxAttributeID': 55})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.cacheUpdater')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, '1 rows in table dgmattribs have invalid PKs, removing them')
        self.assertEqual(len(data['attributes']), 1)
        self.assertEqual(data['attributes'][7][0], 50)

    def testDgmeffects(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 7, 'isDefault': False})
        self.dh.data['dgmeffects'].append({'effectID': 7, 'preExpression': 50})
        self.dh.data['dgmeffects'].append({'effectID': 7, 'preExpression': 55})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.cacheUpdater')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, '1 rows in table dgmeffects have invalid PKs, removing them')
        self.assertEqual(len(data['effects']), 1)
        self.assertEqual(data['effects'][7][4], 50)

    def testDgmtypeeffects(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 100, 'isDefault': True})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 100, 'isDefault': False})
        self.dh.data['dgmeffects'].append({'effectID': 100, 'falloffAttributeID': 70})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 1)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.cacheUpdater')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, '1 rows in table dgmtypeeffects have invalid PKs, removing them')
        self.assertEqual(len(data['types']), 1)
        self.assertEqual(data['types'][1][5], 70)

    def testDgmexpressions(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 7, 'isDefault': False})
        self.dh.data['dgmeffects'].append({'effectID': 7, 'preExpression': 5})
        self.dh.data['dgmexpressions'].append({'expressionID': 5, 'operandID': 55})
        self.dh.data['dgmexpressions'].append({'expressionID': 5, 'operandID': 80})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.cacheUpdater')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, '1 rows in table dgmexpressions have invalid PKs, removing them')
        self.assertEqual(len(data['expressions']), 1)
        self.assertEqual(data['expressions'][5][0], 55)
