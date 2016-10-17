# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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


from eos.data.cache_generator import CacheGenerator
from eos.data.cache_object import Modifier
from tests.eos_testcase import EosTestCase
from .environment import DataHandler


class GeneratorTestCase(EosTestCase):
    """
    Additional functionality provided:

    self.dh -- default data handler
    """

    def setUp(self):
        super().setUp()
        self.dh = DataHandler()

    def run_generator(self):
        """
        Run generator and rework data structure into
        keyed tables so it's easier to check.
        """
        generator = CacheGenerator()
        data = generator.run(self.dh)
        keys = {
            'types': 'type_id',
            'attributes': 'attribute_id',
            'effects': 'effect_id',
            'modifiers': 'modifier_id'
        }
        keyed_data = {}
        for table_name in data:
            keyed_table = {}
            key_name = keys[table_name]
            for row in data[table_name]:
                key = row[key_name]
                keyed_table[key] = row
            keyed_data[table_name] = keyed_table
        return keyed_data

    def mod(self, *args, **kwargs):
        """Instantiate and return modifier."""
        return Modifier(*args, **kwargs)
