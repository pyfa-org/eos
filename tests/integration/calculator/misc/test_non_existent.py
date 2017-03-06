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


import logging

from tests.integration.calculator.calculator_testcase import CalculatorTestCase


class TestNonExistent(CalculatorTestCase):
    """Test return value when requesting attribute which isn't set"""

    def test_attribute_data_error(self):
        # Check case when attribute value is available, but
        # cache handler doesn't know about such attribute
        item = IndependentItem(self.ch.type(attributes={105: 20}))
        self.fit.items.add(item)
        self.assertRaises(KeyError, item.attributes.__getitem__, 105)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.fit.calculator.map')
        self.assertEqual(log_record.levelno, logging.ERROR)
        self.assertEqual(log_record.msg, 'unable to fetch metadata for attribute 105, requested for eve type 57')
        self.fit.items.remove(item)
        self.assert_fit_buffers_empty(self.fit)

    def test_absent_base_value_error(self):
        # Check case when default value of attribute cannot be
        # determined. and eve type doesn't define any value either
        attr = self.ch.attribute()
        item = IndependentItem(self.ch.type())
        self.fit.items.add(item)
        self.assertRaises(KeyError, item.attributes.__getitem__, attr.id)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.fit.calculator.map')
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(log_record.msg, 'unable to find base value for attribute 89 on eve type 649')
        self.fit.items.remove(item)
        self.assert_fit_buffers_empty(self.fit)

    def test_absent_default_value(self):
        # Default value should be used if attribute
        # value is not available on eve type
        attr = self.ch.attribute(default_value=5.6)
        item = IndependentItem(self.ch.type())
        self.fit.items.add(item)
        self.assertAlmostEqual(item.attributes[attr.id], 5.6)
        self.fit.items.remove(item)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)
