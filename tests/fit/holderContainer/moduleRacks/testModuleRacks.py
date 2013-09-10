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


from unittest.mock import Mock

from eos.fit.holder.container import ModuleRacks
from eos.tests.fit.holderContainer.containerTestCase import ContainerTestCase


class TestContainerModuleRacks(ContainerTestCase):

    def setUp(self):
        ContainerTestCase.setUp(self)
        self.holder1 = Mock(spec_set=())
        self.holder2 = Mock(spec_set=())
        self.holder3 = Mock(spec_set=())
        self.holder4 = Mock(spec_set=())
        self.holder5 = Mock(spec_set=())
        self.holder6 = Mock(spec_set=())
        self.highRack = [self.holder1, None, None, self.holder2]
        self.medRack = [None, self.holder3, None, None, self.holder4]
        self.lowRack = [self.holder5, None, None, None, self.holder6]
        self.modules = ModuleRacks(high=self.highRack, med=self.medRack, low=self.lowRack)

    def testRackAccessibility(self):
        self.assertIs(self.modules.high, self.highRack)
        self.assertIs(self.modules.med, self.medRack)
        self.assertIs(self.modules.low, self.lowRack)

    def testHoldersLen(self):
        moduleHolders = self.modules.holders()
        self.assertEqual(len(moduleHolders), 6)
        self.highRack.remove(self.holder1)
        self.assertEqual(len(moduleHolders), 5)
        self.medRack.remove(self.holder3)
        self.assertEqual(len(moduleHolders), 4)
        self.lowRack.append(self.holder1)
        self.assertEqual(len(moduleHolders), 5)

    def testHoldersIter(self):
        moduleHolders = self.modules.holders()
        expected = [self.holder1, self.holder2, self.holder3,
                    self.holder4, self.holder5, self.holder6]
        self.assertEqual(list(moduleHolders), expected)
        self.highRack.remove(self.holder1)
        expected = [self.holder2, self.holder3, self.holder4,
                    self.holder5, self.holder6]
        self.assertEqual(list(moduleHolders), expected)
        self.medRack.remove(self.holder3)
        expected = [self.holder2, self.holder4, self.holder5,
                    self.holder6]
        self.assertEqual(list(moduleHolders), expected)
        self.lowRack.append(self.holder1)
        expected = [self.holder2, self.holder4, self.holder5,
                    self.holder6, self.holder1]
        self.assertEqual(list(moduleHolders), expected)

    def testHolderContains(self):
        moduleHolders = self.modules.holders()
        self.assertFalse(None in moduleHolders)
        self.assertTrue(self.holder1 in moduleHolders)
        self.assertTrue(self.holder2 in moduleHolders)
        self.highRack.remove(self.holder1)
        self.assertFalse(self.holder1 in moduleHolders)
        self.assertTrue(self.holder2 in moduleHolders)
        self.assertTrue(self.holder3 in moduleHolders)
        self.assertTrue(self.holder4 in moduleHolders)
        self.medRack.remove(self.holder3)
        self.assertFalse(self.holder3 in moduleHolders)
        self.assertTrue(self.holder4 in moduleHolders)
        self.assertTrue(self.holder5 in moduleHolders)
        self.assertTrue(self.holder6 in moduleHolders)
        self.assertFalse(self.holder1 in moduleHolders)
        self.lowRack.append(self.holder1)
        self.assertTrue(self.holder5 in moduleHolders)
        self.assertTrue(self.holder6 in moduleHolders)
        self.assertTrue(self.holder1 in moduleHolders)
        self.assertFalse(None in moduleHolders)
