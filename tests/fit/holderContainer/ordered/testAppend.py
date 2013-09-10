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


class TestContainerOrderedAppend(ContainerTestCase):

    def setUp(self):
        ContainerTestCase.setUp(self)
        self.fitMock = self._setupContainerCheck()
        self.container = HolderList(self.fitMock)

    def testHolder(self):
        container = self.container
        fitMock = self.fitMock
        holder1 = Mock(spec_set=())
        holder2 = Mock(spec_set=())
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
        self.assertObjectBuffersEmpty(container)

    def testHolderFailure(self):
        container = self.container
        fitMock = self.fitMock
        holder1 = Mock(spec_set=())
        holder2 = Mock(spec_set=())
        container.append(holder1)
        fitMock._addHolder.side_effect = HolderAddError(holder2)
        self.assertRaises(ValueError, container.append, holder2)
        # Make sure it wasn't added even as None
        self.assertEqual(len(container), 1)
        self.assertIs(container[0], holder1)
        container.remove(holder1)
        self.assertEqual(len(fitMock.mock_calls), 3)
        self.assertObjectBuffersEmpty(container)
