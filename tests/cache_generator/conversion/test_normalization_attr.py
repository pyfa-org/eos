#===============================================================================
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
#===============================================================================


from eos.const.eve import Attribute
from eos.tests.cache_generator.generator_testcase import GeneratorTestCase
from eos.tests.environment import Logger


class TestNormalizationAttr(GeneratorTestCase):
    """Check that attribute normalization jobs function as expected"""

    def test_basic_attr_radius(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1, 'radius': 50.0, 'typeName': ''})
        data = self.run_generator()
        self.assertEqual(len(self.log), 1)
        clean_stats = self.log[0]
        self.assertEqual(clean_stats.name, 'eos_test.cache_generator')
        self.assertEqual(clean_stats.levelno, Logger.INFO)
        self.assertEqual(data['types'][1]['attributes'][Attribute.radius], 50.0)

    def test_basic_attr_mass(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1, 'mass': 5.0, 'typeName': ''})
        data = self.run_generator()
        self.assertEqual(len(self.log), 1)
        clean_stats = self.log[0]
        self.assertEqual(clean_stats.name, 'eos_test.cache_generator')
        self.assertEqual(clean_stats.levelno, Logger.INFO)
        self.assertEqual(data['types'][1]['attributes'][Attribute.mass], 5.0)

    def test_basic_attr_volume(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1, 'volume': 500.0, 'typeName': ''})
        data = self.run_generator()
        self.assertEqual(len(self.log), 1)
        clean_stats = self.log[0]
        self.assertEqual(clean_stats.name, 'eos_test.cache_generator')
        self.assertEqual(clean_stats.levelno, Logger.INFO)
        self.assertEqual(data['types'][1]['attributes'][Attribute.volume], 500.0)

    def test_basic_attr_capacity(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1, 'capacity': 0.5, 'typeName': ''})
        data = self.run_generator()
        self.assertEqual(len(self.log), 1)
        clean_stats = self.log[0]
        self.assertEqual(clean_stats.name, 'eos_test.cache_generator')
        self.assertEqual(clean_stats.levelno, Logger.INFO)
        self.assertEqual(data['types'][1]['attributes'][Attribute.capacity], 0.5)
