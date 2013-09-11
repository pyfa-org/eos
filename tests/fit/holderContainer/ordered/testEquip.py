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
from eos.tests.fit.holderContainer.containerTestCase import ContainerTestCase


class TestContainerOrderedEquip(ContainerTestCase):

    def setUp(self):
        ContainerTestCase.setUp(self)
        self.fitMock = self._setupContainerCheck()
        self.container = HolderList(self.fitMock)

    def testHolderToEmpty(self):
        container = self.container
        fitMock = self.fitMock
        holder = Mock(spec_set=())
        self.assertEqual(len(container), 0)
        fitCallsBefore = len(fitMock.mock_calls)
        container.equip(holder)
        fitCallsAfter = len(fitMock.mock_calls)
        self.assertEqual(fitCallsAfter - fitCallsBefore, 1)
        self.assertEqual(fitMock.method_calls[-1], call._addHolder(holder))
        self.assertEqual(len(container), 1)
        self.assertIs(container[0], holder)
        container.remove(holder)
        self.assertObjectBuffersEmpty(container)

    def testHolderSolid(self):
        # Check case when all slots of list are filled
        container = self.container
        fitMock = self.fitMock
        holder1 = Mock(spec_set=())
        holder2 = Mock(spec_set=())
        holder3 = Mock(spec_set=())
        container.append(holder1)
        container.append(holder2)
        self.assertEqual(len(container), 2)
        fitCallsBefore = len(fitMock.mock_calls)
        container.equip(holder3)
        fitCallsAfter = len(fitMock.mock_calls)
        self.assertEqual(fitCallsAfter - fitCallsBefore, 1)
        self.assertEqual(fitMock.method_calls[-1], call._addHolder(holder3))
        self.assertEqual(len(container), 3)
        self.assertIs(container[2], holder3)
        container.remove(holder1)
        container.remove(holder2)
        container.remove(holder3)
        self.assertObjectBuffersEmpty(container)

    def testHolderFirstHole(self):
        # Check that leftmost empty slot is taken
        container = self.container
        fitMock = self.fitMock
        holder1 = Mock(spec_set=())
        holder2 = Mock(spec_set=())
        holder3 = Mock(spec_set=())
        holder4 = Mock(spec_set=())
        container.append(holder1)
        container.insert(3, holder2)
        container.insert(6, holder3)
        self.assertEqual(len(container), 7)
        self.assertIsNone(container[1])
        self.assertIsNone(container[2])
        self.assertIsNone(container[4])
        self.assertIsNone(container[5])
        fitCallsBefore = len(fitMock.mock_calls)
        container.equip(holder4)
        fitCallsAfter = len(fitMock.mock_calls)
        self.assertEqual(fitCallsAfter - fitCallsBefore, 1)
        self.assertEqual(fitMock.method_calls[-1], call._addHolder(holder4))
        self.assertEqual(len(container), 7)
        self.assertIs(container[1], holder4)
        container.remove(holder1)
        container.remove(holder2)
        container.remove(holder3)
        container.remove(holder4)
        self.assertObjectBuffersEmpty(container)

    def testHolderFailure(self):
        container = self.container
        fitMock = self.fitMock
        holder1 = Mock(spec_set=())
        holder2 = Mock(spec_set=())
        container.append(holder1)
        self.assertEqual(len(container), 1)
        fitMock._addHolder.side_effect = HolderAddError(holder2)
        fitCallsBefore = len(fitMock.mock_calls)
        self.assertRaises(ValueError, container.equip, holder2)
        fitCallsAfter = len(fitMock.mock_calls)
        self.assertEqual(fitCallsAfter - fitCallsBefore, 1)
        self.assertEqual(fitMock.method_calls[-1], call._addHolder(holder2))
        self.assertEqual(len(container), 1)
        self.assertIs(container[0], holder1)
        container.remove(holder1)
        self.assertObjectBuffersEmpty(container)
