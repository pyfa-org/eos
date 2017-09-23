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


from eos.data.cachable_builder import CachableBuilder
from eos.eve_object.modifier import DogmaModifier
from tests.eos_testcase import EosTestCase
from .environment import DataHandler


class CachableBuilderTestCase(EosTestCase):
    """
    Additional functionality provided:

    self.dh -- default data handler
    self.run_builder -- shortcut to runing cachable object
        builder on the data provided by data handler self.dh
    self.mod -- instantiate dogma modifier
    """

    def setUp(self):
        super().setUp()
        self.dh = DataHandler()

    def run_builder(self):
        """
        Run builder and store data on test object so that
        it's easier to access.
        """
        self.types, self.attributes, self.effects = CachableBuilder.run(self.dh)

    def mod(self, *args, **kwargs):
        return DogmaModifier(*args, **kwargs)
