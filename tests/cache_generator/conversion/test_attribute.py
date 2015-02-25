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


from eos.tests.cache_generator.generator_testcase import GeneratorTestCase
from eos.tests.environment import Logger


class TestConversionAttribute(GeneratorTestCase):
    """
    Appropriate data should be saved into appropriate
    indexes of object representing attribute.
    """

    def test_fields(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1, 'typeName': ''})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 111, 'value': 8.2})
        self.dh.data['dgmattribs'].append({
            'maxAttributeID': 84, 'randomField': None, 'stackable': True,
            'defaultValue': 0.0, 'attributeID': 111, 'highIsGood': False,
            'attributeName': ''
        })
        data = self.run_generator()
        self.assertEqual(len(self.log), 2)
        literal_stats = self.log[0]
        self.assertEqual(literal_stats.name, 'eos_test.cache_generator')
        self.assertEqual(literal_stats.levelno, Logger.INFO)
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos_test.cache_generator')
        self.assertEqual(clean_stats.levelno, Logger.INFO)
        self.assertEqual(len(data['attributes']), 1)
        self.assertIn(111, data['attributes'])
        expected = {
            'attribute_id': 111, 'max_attribute': 84, 'default_value': 0.0,
            'high_is_good': False, 'stackable': True
        }
        self.assertEqual(data['attributes'][111], expected)
