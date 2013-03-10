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


from unittest.mock import Mock, call

from eos.fit.holder.container import HolderSet
from eos.tests.fit.fitTestCase import FitTestCase
from eos.tests.fit.environment import Holder


class TestContainerUnordered(FitTestCase):

    def setUp(self):
        FitTestCase.setUp(self)
        self.fitMock = Mock()
        self.container = HolderSet(self.fitMock)
        # To make sure item is properly added to fit, we check that
        # when container asks fit to add holder to services. holder
        # already needs to pass membership check within container
        self.fitMock._addHolder.side_effect = lambda holder: self.assertIn(holder, self.container)
        self.fitMock._removeHolder.side_effect = lambda holder: self.assertIn(holder, self.container)

    def testAddRemoveHolder(self):
        container = self.container
        fitMock = self.fitMock
        holder = Holder()
        container.add(holder)
        self.assertEqual(len(fitMock.mock_calls), 1)
        self.assertEqual(fitMock.method_calls[0], call._addHolder(holder))
        container.remove(holder)
        self.assertEqual(len(fitMock.mock_calls), 2)
        self.assertEqual(fitMock.method_calls[1], call._removeHolder(holder))
        self.assertBuffersEmpty(container)

    def testAddAgain(self):
        container = self.container
        fitMock = self.fitMock
        holder = Holder()
        container.add(holder)
        container.add(holder)
        container.remove(holder)
        # Adding holder to container twice shouldn't
        # generate additional calls
        self.assertEqual(len(fitMock.mock_calls), 2)
        self.assertBuffersEmpty(container)

    def testRemoveFail(self):
        container = self.container
        fitMock = self.fitMock
        holder1 = Holder()
        holder2 = Holder()
        container.add(holder1)
        container.add(holder2)
        container.remove(holder2)
        self.assertRaises(KeyError, container.remove, holder2)
        # Make sure holder1 wasn't removed
        container.remove(holder1)
        # Make sure attempt to remove holder which doesn't
        # belong to container didn't generate external call
        self.assertEqual(len(fitMock.mock_calls), 4)
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
