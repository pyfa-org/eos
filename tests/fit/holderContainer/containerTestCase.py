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

from eos.tests.fit.fitTestCase import FitTestCase


class ContainerTestCase(FitTestCase):
    """
    Additional functionality provided:

    _setupContainerCheck -- method which creates fitMock,
    mock which replaces real Fit object for testing of
    holder containers. When holder asks it to register/
    unregister holder, it also checks if holder belongs
    to self.container (which should be set in child test
    cases) at the time of request
    _setupDirectCheck -- method which takes passed fit
    and attribute name, and when holder is being added
    to fit, it checks if holder is already assigned to
    passed attribute.
    """

    def _setupContainerCheck(self):
        fitMock = Mock()
        # To make sure item is properly added to fit, we check that
        # when container asks fit to add holder to services. holder
        # already needs to pass membership check within container
        fitMock._addHolder.side_effect = lambda holder: self.assertIn(holder, self.container)
        fitMock._removeHolder.side_effect = lambda holder: self.assertIn(holder, self.container)
        return fitMock

    def _setupDirectCheck(self, fit, attrName):
        fit._addHolder = Mock()
        fit._addHolder.side_effect = lambda holder: self.assertIs(getattr(fit, attrName), holder)
        fit._removeHolder = Mock()
        fit._removeHolder.side_effect = lambda holder: self.assertIs(getattr(fit, attrName), holder)
