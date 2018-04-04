# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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


class TestAttrValue(EveObjBuilderTestCase):
    """Ensure that attributes values are properly checked."""

    logger_name = 'eos.eve_obj_builder.validator_preconv'

    def test_int(self):
        self.dh.data['evetypes'].append(
            {'typeID': 1, 'groupID': 1})
        self.dh.data['dgmtypeattribs'].append(
            {'typeID': 1, 'attributeID': 5, 'value': 8})
        self.run_builder()
        self.assertEqual(len(self.types), 1)
        self.assertEqual(self.types[1].attrs[5], 8)
        self.assertEqual(len(self.get_log(name=self.logger_name)), 0)

    def test_float(self):
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1})
        self.dh.data['dgmtypeattribs'].append(
            {'typeID': 1, 'attributeID': 5, 'value': 8.5})
        self.run_builder()
        self.assertEqual(len(self.types), 1)
        self.assertEqual(self.types[1].attrs[5], 8.5)
        self.assertEqual(len(self.get_log(name=self.logger_name)), 0)

    def test_other(self):
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1})
        self.dh.data['dgmtypeattribs'].append(
            {'typeID': 1, 'attributeID': 5, 'value': None})
        self.run_builder()
        self.assertEqual(len(self.types), 1)
        self.assertIn(1, self.types)
        self.assertEqual(len(self.types[1].attrs), 0)
        log = self.get_log(name=self.logger_name)
        self.assertEqual(len(log), 1)
        log_record = log[0]
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(
            log_record.msg,
            '1 attribute rows have non-numeric value, removing them')

    def test_cleanup(self):
        # Make sure cleanup runs before check being tested
        self.dh.data['evetypes'].append({'typeID': 1})
        self.dh.data['dgmtypeattribs'].append(
            {'typeID': 1, 'attributeID': 5, 'value': None})
        self.run_builder()
        self.assertEqual(len(self.types), 0)
        self.assertEqual(len(self.get_log(name=self.logger_name)), 0)
