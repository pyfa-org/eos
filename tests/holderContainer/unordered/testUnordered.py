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


from unittest.mock import call

from eos.fit.exception import HolderAddError
from eos.fit.holder.container import HolderSet
from eos.tests.holderContainer.containerTestCase import ContainerTestCase
from eos.tests.holderContainer.environment import Holder


class TestContainerUnordered(ContainerTestCase):

    def setUp(self):
        ContainerTestCase.setUp(self)
        self.container = HolderSet(self.fitMock)

    def testAddRemoveHolder(self):
        container = self.container
        fitMock = self.fitMock
        holder1 = Holder()
        holder2 = Holder()
        self.assertEqual(len(fitMock.mock_calls), 0)
        container.add(holder1)
        self.assertEqual(len(fitMock.mock_calls), 1)
        self.assertEqual(fitMock.method_calls[0], call._addHolder(holder1))
        container.add(holder2)
        self.assertEqual(len(fitMock.mock_calls), 2)
        self.assertEqual(fitMock.method_calls[1], call._addHolder(holder2))
        container.remove(holder1)
        self.assertEqual(len(fitMock.mock_calls), 3)
        self.assertEqual(fitMock.method_calls[2], call._removeHolder(holder1))
        container.remove(holder2)
        self.assertEqual(len(fitMock.mock_calls), 4)
        self.assertEqual(fitMock.method_calls[3], call._removeHolder(holder2))
        self.assertBuffersEmpty(container)

    def testAddHolderFailure(self):
        container = self.container
        fitMock = self.fitMock
        holder1 = Holder()
        holder2 = Holder()
        container.add(holder1)
        fitMock._addHolder.side_effect = HolderAddError(holder2)
        self.assertRaises(ValueError, container.add, holder2)
        self.assertTrue(holder1 in container)
        container.remove(holder1)
        self.assertEqual(len(fitMock.mock_calls), 3)
        self.assertEqual(len(container), 0)
        self.assertBuffersEmpty(container)

    def testRemoveHolderFailure(self):
        container = self.container
        fitMock = self.fitMock
        holder1 = Holder()
        holder2 = Holder()
        container.add(holder1)
        container.add(holder2)
        container.remove(holder2)
        self.assertRaises(KeyError, container.remove, holder2)
        self.assertTrue(holder1 in container)
        container.remove(holder1)
        self.assertEqual(len(fitMock.mock_calls), 4)
        self.assertEqual(len(container), 0)
        self.assertBuffersEmpty(container)

    def testLen(self):
        container = self.container
        holder1 = Holder()
        holder2 = Holder()
        self.assertEqual(len(container), 0)
        container.add(holder1)
        self.assertEqual(len(container), 1)
        container.add(holder2)
        self.assertEqual(len(container), 2)
        container.remove(holder1)
        self.assertEqual(len(container), 1)
        container.remove(holder2)
        self.assertEqual(len(container), 0)
        self.assertBuffersEmpty(container)

    def testContains(self):
        container = self.container
        holder1 = Holder()
        holder2 = Holder()
        self.assertFalse(holder1 in container)
        self.assertFalse(holder2 in container)
        container.add(holder1)
        self.assertTrue(holder1 in container)
        self.assertFalse(holder2 in container)
        container.add(holder2)
        self.assertTrue(holder1 in container)
        self.assertTrue(holder2 in container)
        container.remove(holder1)
        self.assertFalse(holder1 in container)
        self.assertTrue(holder2 in container)
        container.remove(holder2)
        self.assertFalse(holder1 in container)
        self.assertFalse(holder2 in container)
        self.assertBuffersEmpty(container)

    def testIter(self):
        container = self.container
        holder1 = Holder()
        holder2 = Holder()
        self.assertEqual(set(holder for holder in container), set())
        container.add(holder1)
        self.assertEqual(set(holder for holder in container), {holder1})
        container.add(holder2)
        self.assertEqual(set(holder for holder in container), {holder1, holder2})
        container.remove(holder1)
        self.assertEqual(set(holder for holder in container), {holder2})
        container.remove(holder2)
        self.assertEqual(set(holder for holder in container), set())
        self.assertBuffersEmpty(container)

    def testClear(self):
        container = self.container
        holder1 = Holder()
        holder2 = Holder()
        container.add(holder1)
        container.add(holder2)
        container.clear()
        self.assertEqual(len(container), 0)
        self.assertBuffersEmpty(container)
