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
from eos.fit.holder.container import HolderList, SlotTakenError
from eos.tests.fit.holderContainer.containerTestCase import ContainerTestCase


class TestContainerOrderedPlace(ContainerTestCase):

    def setUp(self):
        ContainerTestCase.setUp(self)
        self.fitMock = self._setupContainerCheck()
        self.container = HolderList(self.fitMock)

    def testHolderOutside(self):
        container = self.container
        fitMock = self.fitMock
        holder1 = Mock(spec_set=())
        holder2 = Mock(spec_set=())
        container.append(holder1)
        self.assertEqual(len(container), 1)
        self.assertRaises(IndexError, container.__getitem__, 3)
        fitCallsBefore = len(fitMock.mock_calls)
        container.place(3, holder2)
        fitCallsAfter = len(fitMock.mock_calls)
        self.assertEqual(fitCallsAfter - fitCallsBefore, 1)
        self.assertEqual(fitMock.method_calls[-1], call._addHolder(holder2))
        self.assertIs(container[3], holder2)
        self.assertEqual(len(container), 4)
        container.remove(holder1)
        container.remove(holder2)
        self.assertObjectBuffersEmpty(container)

    def testHolderOntoNone(self):
        container = self.container
        fitMock = self.fitMock
        holder1 = Mock(spec_set=())
        holder2 = Mock(spec_set=())
        holder3 = Mock(spec_set=())
        container.append(holder1)
        container.insert(3, holder2)
        self.assertIsNone(container[1])
        self.assertEqual(len(container), 4)
        fitCallsBefore = len(fitMock.mock_calls)
        container.place(1, holder3)
        fitCallsAfter = len(fitMock.mock_calls)
        self.assertEqual(fitCallsAfter - fitCallsBefore, 1)
        self.assertEqual(fitMock.method_calls[-1], call._addHolder(holder3))
        self.assertIs(container[1], holder3)
        self.assertEqual(len(container), 4)
        container.remove(holder1)
        container.remove(holder2)
        container.remove(holder3)
        self.assertObjectBuffersEmpty(container)

    def testHolderOntoHolder(self):
        container = self.container
        fitMock = self.fitMock
        holder1 = Mock(spec_set=())
        holder2 = Mock(spec_set=())
        container.append(holder1)
        self.assertIs(container[0], holder1)
        self.assertEqual(len(container), 1)
        fitCallsBefore = len(fitMock.mock_calls)
        self.assertRaises(SlotTakenError, container.place, 0, holder2)
        fitCallsAfter = len(fitMock.mock_calls)
        self.assertEqual(fitCallsAfter - fitCallsBefore, 0)
        self.assertIs(container[0], holder1)
        container.remove(holder1)
        self.assertObjectBuffersEmpty(container)

    def testHolderOutsideFailure(self):
        container = self.container
        fitMock = self.fitMock
        holder = Mock(spec_set=())
        fitMock._addHolder.side_effect = HolderAddError(holder)
        fitCallsBefore = len(fitMock.mock_calls)
        self.assertRaises(ValueError, container.place, 2, holder)
        fitCallsAfter = len(fitMock.mock_calls)
        self.assertEqual(fitCallsAfter - fitCallsBefore, 1)
        self.assertEqual(fitMock.method_calls[-1], call._addHolder(holder))
        self.assertEqual(len(container), 0)
        self.assertObjectBuffersEmpty(container)

    def testHolderOntoNoneFailure(self):
        container = self.container
        fitMock = self.fitMock
        holder1 = Mock(spec_set=())
        holder2 = Mock(spec_set=())
        container.insert(1, holder1)
        self.assertEqual(len(container), 2)
        self.assertIsNone(container[0])
        self.assertIs(container[1], holder1)
        fitMock._addHolder.side_effect = HolderAddError(holder2)
        fitCallsBefore = len(fitMock.mock_calls)
        self.assertRaises(ValueError, container.place, 0, holder2)
        fitCallsAfter = len(fitMock.mock_calls)
        self.assertEqual(fitCallsAfter - fitCallsBefore, 1)
        self.assertEqual(fitMock.method_calls[-1], call._addHolder(holder2))
        self.assertEqual(len(container), 2)
        self.assertIsNone(container[0])
        self.assertIs(container[1], holder1)
        container.remove(holder1)
        self.assertObjectBuffersEmpty(container)
