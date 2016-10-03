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


class TestRackCollision(GeneratorTestCase):
    """
    Make sure that rack collision is detected,
    and it is detected after cleanup.
    """

    def setUp(self):
        super().setUp()
        self.item = {'typeID': 1, 'groupID': 1, 'typeName_en-us': ''}
        self.dh.data['evetypes'].append(self.item)
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 13})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 11})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 12})
        self.dh.data['dgmeffects'].append({'effectID': 11})
        self.dh.data['dgmeffects'].append({'effectID': 12})
        self.dh.data['dgmeffects'].append({'effectID': 13})

    def test_collision(self):
        data = self.run_generator()
        self.assertEqual(len(self.log), 3)
        literal_stats = self.log[0]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        log_record = self.log[2]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.checker')
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(log_record.msg, '2 rows contain colliding module racks, removing them')
        self.assertEqual(len(data['types']), 1)
        self.assertIn(1, data['types'])
        type_effects = data['types'][1]['effects']
        self.assertEqual(len(type_effects), 1)
        self.assertIn(13, type_effects)
        self.assertEqual(len(data['effects']), 3)

    def test_cleaned(self):
        del self.item['groupID']
        data = self.run_generator()
        self.assertEqual(len(self.log), 2)
        literal_stats = self.log[0]
        self.assertEqual(literal_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(literal_stats.levelno, logging.INFO)
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertEqual(len(data['types']), 0)
        self.assertEqual(len(data['effects']), 0)
