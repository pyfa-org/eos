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


class TestCleanupTypes(UpdaterTestCase):
    """
    Check which items should stay in the data.
    """

    def testGroupCharacter(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 0)
        self.assertEqual(len(data['types']), 1)
        self.assertIn(1, data['types'])

    def testGroupEffectBeacon(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 920})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 0)
        self.assertEqual(len(data['types']), 1)
        self.assertIn(1, data['types'])

    def testGroupOther(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 50})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 0)
        self.assertEqual(len(data['types']), 0)

    def testGroupCharacterUnpublished(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1, 'published': False})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 0)
        self.assertEqual(len(data['types']), 1)
        self.assertIn(1, data['types'])

    def testCategoryShip(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 50})
        self.dh.data['invgroups'].append({'groupID': 50, 'categoryID': 6})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 0)
        self.assertEqual(len(data['types']), 1)
        self.assertIn(1, data['types'])

    def testCategoryModule(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 50})
        self.dh.data['invgroups'].append({'groupID': 50, 'categoryID': 7})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 0)
        self.assertEqual(len(data['types']), 1)
        self.assertIn(1, data['types'])

    def testCategoryCharge(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 50})
        self.dh.data['invgroups'].append({'groupID': 50, 'categoryID': 8})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 0)
        self.assertEqual(len(data['types']), 1)
        self.assertIn(1, data['types'])

    def testCategorySkill(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 50})
        self.dh.data['invgroups'].append({'groupID': 50, 'categoryID': 16})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 0)
        self.assertEqual(len(data['types']), 1)
        self.assertIn(1, data['types'])

    def testCategoryDrone(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 50})
        self.dh.data['invgroups'].append({'groupID': 50, 'categoryID': 18})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 0)
        self.assertEqual(len(data['types']), 1)
        self.assertIn(1, data['types'])

    def testCategoryImplant(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 50})
        self.dh.data['invgroups'].append({'groupID': 50, 'categoryID': 20})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 0)
        self.assertEqual(len(data['types']), 1)
        self.assertIn(1, data['types'])

    def testCategorySubsystem(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 50})
        self.dh.data['invgroups'].append({'groupID': 50, 'categoryID': 32})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 0)
        self.assertEqual(len(data['types']), 1)
        self.assertIn(1, data['types'])

    def testCategoryOther(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 50})
        self.dh.data['invgroups'].append({'groupID': 50, 'categoryID': 51})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 0)
        self.assertEqual(len(data['types']), 0)

    def testMixed(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 920})
        self.dh.data['invtypes'].append({'typeID': 2, 'groupID': 50})
        self.dh.data['invtypes'].append({'typeID': 3, 'groupID': 20})
        self.dh.data['invgroups'].append({'groupID': 20, 'categoryID': 7})
        self.dh.data['invtypes'].append({'typeID': 4, 'groupID': 80})
        self.dh.data['invgroups'].append({'groupID': 80, 'categoryID': 700})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 0)
        self.assertEqual(len(data['types']), 2)
        self.assertIn(1, data['types'])
        self.assertIn(3, data['types'])
