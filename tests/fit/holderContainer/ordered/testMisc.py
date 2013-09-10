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

from eos.fit.holder.container import HolderList
from eos.tests.fit.holderContainer.containerTestCase import ContainerTestCase


class TestContainerOrderedMisc(ContainerTestCase):

    def setUp(self):
        ContainerTestCase.setUp(self)
        self.fitMock = self._setupContainerCheck()
        self.container = HolderList(self.fitMock)

    def testLen(self):
        container = self.container
        holder1 = Mock(spec_set=())
        holder2 = Mock(spec_set=())
        self.assertEqual(len(container), 0)
        container.append(holder1)
        self.assertEqual(len(container), 1)
        container.place(3, holder2)
        self.assertEqual(len(container), 4)
        container.remove(holder1)
        self.assertEqual(len(container), 3)
        container.remove(holder2)
        self.assertEqual(len(container), 0)
        self.assertBuffersEmpty(container)

    def testContains(self):
        container = self.container
        holder1 = Mock(spec_set=())
        holder2 = Mock(spec_set=())
        self.assertFalse(holder1 in container)
        self.assertFalse(None in container)
        self.assertFalse(holder2 in container)
        container.append(holder1)
        self.assertTrue(holder1 in container)
        self.assertFalse(None in container)
        self.assertFalse(holder2 in container)
        container.place(3, holder2)
        self.assertTrue(holder1 in container)
        self.assertTrue(None in container)
        self.assertTrue(holder2 in container)
        container.remove(holder1)
        self.assertFalse(holder1 in container)
        self.assertTrue(None in container)
        self.assertTrue(holder2 in container)
        container.remove(holder2)
        self.assertFalse(holder1 in container)
        self.assertFalse(None in container)
        self.assertFalse(holder2 in container)
        self.assertBuffersEmpty(container)

    def testIter(self):
        container = self.container
        holder1 = Mock(spec_set=())
        holder2 = Mock(spec_set=())
        self.assertEqual(list(holder for holder in container), [])
        container.append(holder1)
        self.assertEqual(list(holder for holder in container), [holder1])
        container.place(3, holder2)
        self.assertEqual(list(holder for holder in container), [holder1, None, None, holder2])
        container.remove(holder1)
        self.assertEqual(list(holder for holder in container), [None, None, holder2])
        container.remove(holder2)
        self.assertEqual(list(holder for holder in container), [])
        self.assertBuffersEmpty(container)

    def testClear(self):
        container = self.container
        fitMock = self.fitMock
        holder1 = Mock(spec_set=())
        holder2 = Mock(spec_set=())
        container.append(holder1)
        container.place(3, holder2)
        self.assertEqual(len(fitMock.mock_calls), 2)
        container.clear()
        self.assertEqual(len(fitMock.mock_calls), 4)
        newCalls = fitMock.method_calls[2:4]
        self.assertIn(call._removeHolder(holder1), newCalls)
        self.assertIn(call._removeHolder(holder2), newCalls)
        self.assertEqual(len(container), 0)
        self.assertBuffersEmpty(container)

    def testHolderView(self):
        container = self.container
        view = container.holders()
        holder1 = Mock(spec_set=())
        holder2 = Mock(spec_set=())
        self.assertEqual(len(view), 0)
        self.assertEqual(list(view), [])
        self.assertFalse(holder1 in view)
        self.assertFalse(holder2 in view)
        self.assertFalse(None in view)
        container.append(holder1)
        self.assertEqual(len(view), 1)
        self.assertEqual(list(view), [holder1])
        self.assertTrue(holder1 in view)
        self.assertFalse(holder2 in view)
        self.assertFalse(None in view)
        container.place(3, holder2)
        self.assertEqual(len(view), 2)
        self.assertEqual(list(view), [holder1, holder2])
        self.assertTrue(holder1 in view)
        self.assertTrue(holder2 in view)
        self.assertFalse(None in view)
        container.free(holder1)
        self.assertEqual(len(view), 1)
        self.assertEqual(list(view), [holder2])
        self.assertFalse(holder1 in view)
        self.assertTrue(holder2 in view)
        self.assertFalse(None in view)
        container.free(holder2)
        self.assertEqual(len(view), 0)
        self.assertEqual(list(view), [])
        self.assertFalse(holder1 in view)
        self.assertFalse(holder2 in view)
        self.assertFalse(None in view)
        self.assertBuffersEmpty(container)
