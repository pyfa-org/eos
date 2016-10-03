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


import logging

from tests.cache_generator.generator_testcase import GeneratorTestCase


class TestConversionType(GeneratorTestCase):
    """
    Appropriate data should be saved into appropriate
    indexes of object representing effect.
    """

    def test_fields(self):
        self.dh.data['evetypes'].append({'randomField': 66, 'typeID': 1, 'groupID': 6, 'typeName_en-us': ''})
        self.dh.data['evegroups'].append({'categoryID': 16, 'groupID': 6, 'groupName_en-us': ''})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 5, 'value': 10.0})
        self.dh.data['dgmtypeattribs'].append({'attributeID': 80, 'typeID': 1, 'value': 180.0})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 111, 'isDefault': True})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 1111, 'isDefault': False})
        self.dh.data['dgmeffects'].append({
            'effectID': 111, 'effectCategory': 8, 'isOffensive': True, 'isAssistance': False,
            'fittingUsageChanceAttributeID': 96, 'preExpression': None, 'postExpression': None
        })
        self.dh.data['dgmeffects'].append({
            'effectID': 1111, 'effectCategory': 85, 'isOffensive': False, 'isAssistance': True,
            'fittingUsageChanceAttributeID': 41, 'preExpression': None, 'postExpression': None
        })
        data = self.run_generator()
        self.assertEqual(len(self.log), 2)
        literal_stats = self.log[0]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertEqual(len(data['types']), 1)
        self.assertIn(1, data['types'])
        type_row = data['types'][1]
        self.assertEqual(len(type_row), 6)
        self.assertEqual(type_row['group'], 6)
        self.assertEqual(type_row['category'], 16)
        type_attributes = type_row['attributes']
        self.assertEqual(len(type_attributes), 2)
        self.assertEqual(type_attributes[5], 10.0)
        self.assertEqual(type_attributes[80], 180.0)
        type_effects = type_row['effects']
        self.assertEqual(len(type_effects), 2)
        self.assertIn(111, type_effects)
        self.assertIn(1111, type_effects)
        type_defeff = type_row['default_effect']
        self.assertEqual(type_defeff, 111)
