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
from eos.tests.holderContainer.containerTestCase import HolderContainerTestCase
from eos.tests.holderContainer.environment import Holder


class TestUnorderedAdd(HolderContainerTestCase):

    def testHolder(self):
        fitMock = Mock()
        holder = Holder()
        # To make sure item is properly added to fit, we check that
        # when container asks fit to add holder to services. holder
        # already needs to pass membership check within container
        fitMock._addHolder.side_effect = lambda holder: self.assertIn(holder, container)
        fitMock._removeHolder.side_effect = lambda holder: self.assertIn(holder, container)
        container = HolderSet(fitMock)
        container.add(holder)
        self.assertEqual(len(fitMock.mock_calls), 1)
        self.assertEqual(fitMock.method_calls[0], call._addHolder(holder))
        container.remove(holder)
        self.assertEqual(len(fitMock.mock_calls), 2)
        self.assertEqual(fitMock.method_calls[1], call._removeHolder(holder))
        self.assertBuffersEmpty(container)
