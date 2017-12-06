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

from tests.eve_obj_builder.testcase import EveObjBuilderTestCase


class TestRackCollision(EveObjBuilderTestCase):
    """Check that each item can have has max 1 rack effect."""

    logger_name = 'eos.data.eve_obj_builder.validator_preconv'

    def setUp(self):
        EveObjBuilderTestCase.setUp(self)
        self.type = {'typeID': 1, 'groupID': 1}
        self.dh.data['evetypes'].append(self.type)
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 13})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 11})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 12})
        self.dh.data['dgmeffects'].append({'effectID': 11})
        self.dh.data['dgmeffects'].append({'effectID': 12})
        self.dh.data['dgmeffects'].append({'effectID': 13})

    def test_collision(self):
        self.run_builder()
        self.assertEqual(len(self.types), 1)
        self.assertIn(1, self.types)
        type_effects = self.types[1].effects
        self.assertEqual(len(type_effects), 1)
        self.assertIn(13, type_effects)
        self.assertEqual(len(self.effects), 3)
        log = self.get_log(name=self.logger_name)
        self.assertEqual(len(log), 1)
        log_record = log[0]
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(
            log_record.msg,
            '2 rows contain colliding module racks, removing them')

    def test_cleaned(self):
        del self.type['groupID']
        self.run_builder()
        self.assertEqual(len(self.types), 0)
        self.assertEqual(len(self.effects), 0)
        self.assertEqual(len(self.get_log(name=self.logger_name)), 0)
