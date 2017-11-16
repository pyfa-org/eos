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

from eos import *
from tests.integration.calculator.calculator_testcase import CalculatorTestCase


class TestNonExistent(CalculatorTestCase):
    """Test return value when requesting attribute which isn't set."""

    def test_attr_data_error(self):
        # Check case when attribute value is available, but cache handler
        # doesn't know about such attribute
        item_type = self.mktype(attrs={105: 20})
        item = Implant(item_type.id)
        self.fit.implants.add(item)
        # Action
        with self.assertRaises(KeyError):
            item.attrs[105]
        # Verification
        log = self.get_log()
        self.assertEqual(len(log), 1)
        log_record = log[0]
        self.assertEqual(log_record.name, 'eos.fit.calculator.map')
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(
            log_record.msg,
            'unable to fetch metadata for attribute 105,'
            ' requested for item type {}'.format(item_type.id))
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)

    def test_absent_base_value_error(self):
        # Check case when default value of attribute cannot be determined. and
        # item type doesn't define any value either
        attr = self.mkattr()
        item_type = self.mktype()
        item = Implant(item_type.id)
        self.fit.implants.add(item)
        # Action
        with self.assertRaises(KeyError):
            item.attrs[attr.id]
        # Verification
        log = self.get_log()
        self.assertEqual(len(log), 1)
        log_record = log[0]
        self.assertEqual(log_record.name, 'eos.fit.calculator.map')
        self.assertEqual(log_record.levelno, logging.INFO)
        self.assertEqual(
            log_record.msg,
            'unable to find base value for attribute {} '
            'on item type {}'.format(attr.id, item_type.id))
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)

    def test_absent_default_value(self):
        # Default value should be used if attribute value is not available on
        # item type
        attr = self.mkattr(default_value=5.6)
        item = Implant(self.mktype().id)
        # Action
        self.fit.implants.add(item)
        # Verification
        self.assertAlmostEqual(item.attrs[attr.id], 5.6)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
