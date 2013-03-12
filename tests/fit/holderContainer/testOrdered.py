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

    def testAppendRemoveHolder(self):
        container = self.container
        fitMock = self.fitMock
        holder = Holder()
        container.append(holder)
        self.assertEqual(len(fitMock.mock_calls), 1)
        self.assertEqual(fitMock.method_calls[0], call._addHolder(holder))
        container.remove(holder)
        self.assertEqual(len(fitMock.mock_calls), 2)
        self.assertEqual(fitMock.method_calls[1], call._removeHolder(holder))
        self.assertBuffersEmpty(container)
