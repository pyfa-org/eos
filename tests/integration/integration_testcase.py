# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2017 Anton Vorobyov
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
# ===============================================================================


from copy import copy

from eos.const.eve import Type
from eos.data.source import SourceManager, Source
from tests.eos_testcase import EosTestCase


class IntegrationTestCase(EosTestCase):
    """
    Additional functionality provided:

    self.assert_fit_buffers_empty -- checks if fit contains anything
        in object containers which are designed to hold temporary data
    """

    def setUp(self):
        super().setUp()
        # Replace existing sources with test source
        self.__sources = copy(SourceManager._sources)
        self.__default_source = SourceManager.default
        SourceManager._sources.clear()
        test_source = Source('test', self.ch)
        SourceManager._sources['test'] = test_source
        SourceManager.default = test_source
        # Instantiate character type, as it's used in every test
        self.ch.type(type_id=Type.character_static)

    def tearDown(self):
        # Revert source change
        SourceManager._sources.clear()
        SourceManager._sources.update(self.__sources)
        SourceManager.default = self.__default_source
        super().tearDown()

    def assert_fit_buffers_empty(self, fit):
        # TODO: check all known fit containers, they should be empty
        pass
