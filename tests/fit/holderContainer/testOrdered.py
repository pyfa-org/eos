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

from eos.fit.exception import HolderAddError
from eos.fit.holder.container import HolderList
from eos.tests.fit.fitTestCase import FitTestCase
from eos.tests.fit.environment import Holder


class TestContainerOrdered(FitTestCase):

    def setUp(self):
        FitTestCase.setUp(self)
        self.fitMock = Mock()
        self.container = HolderList(self.fitMock)
        # To make sure item is properly added to fit, we check that
        # when container asks fit to add holder to services. holder
        # already needs to pass membership check within container
        self.fitMock._addHolder.side_effect = lambda holder: self.assertIn(holder, self.container)
        self.fitMock._removeHolder.side_effect = lambda holder: self.assertIn(holder, self.container)

    def testAppendHolder(self):
        container = self.container
        fitMock = self.fitMock
        holder1 = Holder()
        holder2 = Holder()
        self.assertEqual(len(fitMock.mock_calls), 0)
        container.append(holder1)
        self.assertEqual(len(fitMock.mock_calls), 1)
        self.assertEqual(fitMock.method_calls[0], call._addHolder(holder1))
        container.append(holder2)
        self.assertEqual(len(fitMock.mock_calls), 2)
        self.assertEqual(fitMock.method_calls[1], call._addHolder(holder2))
        self.assertIs(container[0], holder1)
        self.assertIs(container[1], holder2)
        container.remove(holder1)
        container.remove(holder2)
        self.assertBuffersEmpty(container)

    def testAppendHolderFailure(self):
        container = self.container
        fitMock = self.fitMock
        holder1 = Holder()
        holder2 = Holder()
        container.append(holder1)
        fitMock._addHolder.side_effect = HolderAddError(holder2)
        self.assertRaises(ValueError, container.append, holder2)
        # Make sure it wasn't added even as None
        self.assertEqual(len(container), 1)
        self.assertIs(container[0], holder1)
        container.remove(holder1)
        self.assertEqual(len(fitMock.mock_calls), 3)
        self.assertBuffersEmpty(container)

    def testInsertHolderToZero(self):
        container = self.container
        fitMock = self.fitMock
        holder1 = Holder()
        holder2 = Holder()
        holder3 = Holder()
        container.append(holder1)
        container.append(holder2)
        self.assertEqual(len(fitMock.mock_calls), 2)
        container.insert(0, holder3)
        self.assertEqual(len(fitMock.mock_calls), 3)
        self.assertEqual(fitMock.method_calls[2], call._addHolder(holder3))
        self.assertEqual(len(container), 3)
        self.assertIs(container[0], holder3)
        self.assertIs(container[1], holder1)
        self.assertIs(container[2], holder2)
        container.remove(holder1)
        container.remove(holder2)
        container.remove(holder3)
        self.assertEqual(len(container), 0)
        self.assertBuffersEmpty(container)

    def testInsertHolderToEnd(self):
        container = self.container
        fitMock = self.fitMock
        holder1 = Holder()
        holder2 = Holder()
        holder3 = Holder()
        container.append(holder1)
        container.append(holder2)
        self.assertEqual(len(fitMock.mock_calls), 2)
        container.insert(2, holder3)
        self.assertEqual(len(fitMock.mock_calls), 3)
        self.assertEqual(fitMock.method_calls[2], call._addHolder(holder3))
        self.assertEqual(len(container), 3)
        self.assertIs(container[0], holder1)
        self.assertIs(container[1], holder2)
        self.assertIs(container[2], holder3)
        container.remove(holder1)
        container.remove(holder2)
        container.remove(holder3)
        self.assertEqual(len(container), 0)
        self.assertBuffersEmpty(container)

    def testInsertHolderOutside(self):
        container = self.container
        fitMock = self.fitMock
        holder1 = Holder()
        holder2 = Holder()
        container.append(holder1)
        self.assertEqual(len(fitMock.mock_calls), 1)
        container.insert(3, holder2)
        self.assertEqual(len(fitMock.mock_calls), 2)
        self.assertEqual(fitMock.method_calls[1], call._addHolder(holder2))
        self.assertEqual(len(container), 4)
        self.assertIs(container[0], holder1)
        self.assertIs(container[1], None)
        self.assertIs(container[2], None)
        self.assertIs(container[3], holder2)
        container.remove(holder1)
        container.remove(holder2)
        self.assertEqual(len(container), 0)
        self.assertBuffersEmpty(container)

    def testInsertHolderFailure(self):
        container = self.container
        fitMock = self.fitMock
        holder1 = Holder()
        holder2 = Holder()
        holder3 = Holder()
        container.append(holder1)
        container.append(holder2)
        self.assertEqual(len(fitMock.mock_calls), 2)
        fitMock._addHolder.side_effect = HolderAddError(holder3)
        self.assertRaises(ValueError, container.insert, 1, holder3)
        self.assertEqual(len(fitMock.mock_calls), 3)
        self.assertEqual(fitMock.method_calls[2], call._addHolder(holder3))
        self.assertEqual(len(container), 2)
        self.assertIs(container[0], holder1)
        self.assertIs(container[1], holder2)
        container.remove(holder1)
        container.remove(holder2)
        self.assertEqual(len(container), 0)
        self.assertBuffersEmpty(container)

    def testInsertNoneInside(self):
        container = self.container
        fitMock = self.fitMock
        holder1 = Holder()
        holder2 = Holder()
        container.append(holder1)
        container.append(holder2)
        self.assertEqual(len(fitMock.mock_calls), 2)
        container.insert(1, None)
        self.assertEqual(len(fitMock.mock_calls), 2)
        self.assertEqual(len(container), 3)
        self.assertIs(container[0], holder1)
        self.assertIs(container[1], None)
        self.assertIs(container[2], holder2)
        container.remove(holder1)
        container.remove(holder2)
        self.assertEqual(len(container), 0)
        self.assertBuffersEmpty(container)

    def testInsertNoneOutside(self):
        container = self.container
        fitMock = self.fitMock
        holder1 = Holder()
        holder2 = Holder()
        container.append(holder1)
        container.append(holder2)
        self.assertEqual(len(fitMock.mock_calls), 2)
        container.insert(6, None)
        self.assertEqual(len(fitMock.mock_calls), 2)
        self.assertEqual(len(container), 2)
        self.assertIs(container[0], holder1)
        self.assertIs(container[1], holder2)
        container.remove(holder1)
        container.remove(holder2)
        self.assertEqual(len(container), 0)
        self.assertBuffersEmpty(container)
