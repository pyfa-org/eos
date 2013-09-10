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


from eos.tests.eosTestCase import EosTestCase
from .environment import Fit


class AttrCalcTestCase(EosTestCase):
    """
    Additional functionality provided:

    self.fit -- precreated fit with self.ch used as cache handler
    self.assertLinkBuffersEmpty -- checks if link tracker buffers
    of passed fit are clear
    """

    def setUp(self):
        EosTestCase.setUp(self)
        self.fit = Fit(self.ch)

    def assertLinkBuffersEmpty(self, fit):
        register = fit._linkTracker._register
        EosTestCase.assertObjectBuffersEmpty(self, register)
