# ==============================================================================
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
# ==============================================================================


import logging

from eos.const.eve import AttributeId
from tests.eve_obj_builder.eve_obj_builder_testcase import EveObjBuilderTestCase


class TestNormalizationIdzing(EveObjBuilderTestCase):
    """Check that symbolic references are converted into IDs"""

    def test_basic_attr_radius(self):
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1, 'radius': 50.0})
        self.run_builder()
        self.assertEqual(len(self.log), 2)
        idzing_stats = self.log[0]
        self.assertEqual(idzing_stats.name, 'eos.data.eve_obj_builder.normalizer')
        self.assertEqual(idzing_stats.levelno, logging.WARNING)
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.eve_obj_builder.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertEqual(self.types[1].attributes[AttributeId.radius], 50.0)

    def test_basic_attr_mass(self):
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1, 'mass': 5.0})
        self.run_builder()
        self.assertEqual(len(self.log), 2)
        idzing_stats = self.log[0]
        self.assertEqual(idzing_stats.name, 'eos.data.eve_obj_builder.normalizer')
        self.assertEqual(idzing_stats.levelno, logging.WARNING)
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.eve_obj_builder.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertEqual(self.types[1].attributes[AttributeId.mass], 5.0)

    def test_basic_attr_volume(self):
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1, 'volume': 500.0})
        self.run_builder()
        self.assertEqual(len(self.log), 2)
        idzing_stats = self.log[0]
        self.assertEqual(idzing_stats.name, 'eos.data.eve_obj_builder.normalizer')
        self.assertEqual(idzing_stats.levelno, logging.WARNING)
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.eve_obj_builder.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertEqual(self.types[1].attributes[AttributeId.volume], 500.0)

    def test_basic_attr_capacity(self):
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1, 'capacity': 0.5})
        self.run_builder()
        self.assertEqual(len(self.log), 2)
        idzing_stats = self.log[0]
        self.assertEqual(idzing_stats.name, 'eos.data.eve_obj_builder.normalizer')
        self.assertEqual(idzing_stats.levelno, logging.WARNING)
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.eve_obj_builder.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertEqual(self.types[1].attributes[AttributeId.capacity], 0.5)

    def test_duplicate_definition(self):
        # Check what happens if attribute is defined in both dgmtypeattribs and evetypes
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1, 'mass': 5.0})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': AttributeId.mass, 'value': 6.0})
        self.run_builder()
        self.assertEqual(len(self.log), 3)
        duplicate_error = self.log[0]
        self.assertEqual(duplicate_error.name, 'eos.data.eve_obj_builder.normalizer')
        self.assertEqual(duplicate_error.levelno, logging.WARNING)
        self.assertEqual(duplicate_error.msg, '1 built-in attributes already have had value in'
                                              ' dgmtypeattribs and were skipped')
        idzing_stats = self.log[1]
        self.assertEqual(idzing_stats.name, 'eos.data.eve_obj_builder.normalizer')
        self.assertEqual(idzing_stats.levelno, logging.WARNING)
        clean_stats = self.log[2]
        self.assertEqual(clean_stats.name, 'eos.data.eve_obj_builder.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertEqual(self.types[1].attributes[AttributeId.mass], 6.0)
