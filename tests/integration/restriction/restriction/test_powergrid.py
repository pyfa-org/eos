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


from eos import *
from eos.const.eos import Restriction, State
from eos.const.eve import Attribute
from tests.integration.restriction.restriction_testcase import RestrictionTestCase


class TestPowerGrid(RestrictionTestCase):
    """Check functionality of power grid restriction"""

    def test_fail_excess_single(self):
        # When ship provides pg output, but single consumer
        # demands for more, error should be raised
        fit = Fit()
        eve_type = self.ch.type(attributes={Attribute.power: 0})
        item = ModuleHigh(eve_type.id, state=State.online)
        item.attributes = {Attribute.power: 50}
        self.add_item(item)
        fit.stats.powergrid.used = 50
        fit.stats.powergrid.output = 40
        restriction_error = self.get_restriction_error(fit, item, Restriction.powergrid)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 40)
        self.assertEqual(restriction_error.total_use, 50)
        self.assertEqual(restriction_error.item_use, 50)
        self.remove_item(item)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_fail_excess_single_other_class(self):
        # Make sure items of all classes are affected
        fit = Fit()
        eve_type = self.ch.type(attributes={Attribute.power: 0})
        item = Implant(eve_type.id, state=State.online)
        item.attributes = {Attribute.power: 50}
        self.add_item(item)
        fit.stats.powergrid.used = 50
        fit.stats.powergrid.output = 40
        restriction_error = self.get_restriction_error(fit, item, Restriction.powergrid)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 40)
        self.assertEqual(restriction_error.total_use, 50)
        self.assertEqual(restriction_error.item_use, 50)
        self.remove_item(item)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_fail_excess_single_undefined_output(self):
        # When stats module does not specify output, make sure
        # it's assumed to be 0
        fit = Fit()
        eve_type = self.ch.type(attributes={Attribute.power: 0})
        item = ModuleHigh(eve_type.id, state=State.online)
        item.attributes = {Attribute.power: 5}
        self.add_item(item)
        fit.stats.powergrid.used = 5
        fit.stats.powergrid.output = None
        restriction_error = self.get_restriction_error(fit, item, Restriction.powergrid)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 0)
        self.assertEqual(restriction_error.total_use, 5)
        self.assertEqual(restriction_error.item_use, 5)
        self.remove_item(item)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_fail_excess_multiple(self):
        # When multiple consumers require less than pg output
        # alone, but in sum want more than total output, it should
        # be erroneous situation
        fit = Fit()
        eve_type = self.ch.type(attributes={Attribute.power: 0})
        item1 = ModuleHigh(eve_type.id, state=State.online)
        item1.attributes = {Attribute.power: 25}
        self.add_item(item1)
        item2 = ModuleHigh(eve_type.id, state=State.online)
        item2.attributes = {Attribute.power: 20}
        self.add_item(item2)
        fit.stats.powergrid.used = 45
        fit.stats.powergrid.output = 40
        restriction_error1 = self.get_restriction_error(fit, item1, Restriction.powergrid)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.output, 40)
        self.assertEqual(restriction_error1.total_use, 45)
        self.assertEqual(restriction_error1.item_use, 25)
        restriction_error2 = self.get_restriction_error(fit, item2, Restriction.powergrid)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.output, 40)
        self.assertEqual(restriction_error2.total_use, 45)
        self.assertEqual(restriction_error2.item_use, 20)
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_fail_excess_modified(self):
        # Make sure modified pg values are taken
        fit = Fit()
        eve_type = self.ch.type(attributes={Attribute.power: 40})
        item = ModuleHigh(eve_type.id, state=State.online)
        item.attributes = {Attribute.power: 100}
        self.add_item(item)
        fit.stats.powergrid.used = 100
        fit.stats.powergrid.output = 50
        restriction_error = self.get_restriction_error(fit, item, Restriction.powergrid)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 50)
        self.assertEqual(restriction_error.total_use, 100)
        self.assertEqual(restriction_error.item_use, 100)
        self.remove_item(item)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_mix_usage_negative(self):
        # If some item has negative usage and pg error is
        # still raised, check it's not raised for item with
        # negative usage
        fit = Fit()
        eve_type = self.ch.type(attributes={Attribute.power: 0})
        item1 = ModuleHigh(eve_type.id, state=State.online)
        item1.attributes = {Attribute.power: 100}
        self.add_item(item1)
        item2 = ModuleHigh(eve_type.id, state=State.online)
        item2.attributes = {Attribute.power: -10}
        self.add_item(item2)
        fit.stats.powergrid.used = 90
        fit.stats.powergrid.output = 50
        restriction_error1 = self.get_restriction_error(fit, item1, Restriction.powergrid)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.output, 50)
        self.assertEqual(restriction_error1.total_use, 90)
        self.assertEqual(restriction_error1.item_use, 100)
        restriction_error2 = self.get_restriction_error(fit, item2, Restriction.powergrid)
        self.assertIsNone(restriction_error2)
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_mix_usage_zero(self):
        # If some item has zero usage and pg error is
        # still raised, check it's not raised for item with
        # zero usage
        fit = Fit()
        eve_type = self.ch.type(attributes={Attribute.power: 0})
        item1 = ModuleHigh(eve_type.id, state=State.online)
        item1.attributes = {Attribute.power: 100}
        self.add_item(item1)
        item2 = ModuleHigh(eve_type.id, state=State.online)
        item2.attributes = {Attribute.power: 0}
        self.add_item(item2)
        fit.stats.powergrid.used = 100
        fit.stats.powergrid.output = 50
        restriction_error1 = self.get_restriction_error(fit, item1, Restriction.powergrid)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.output, 50)
        self.assertEqual(restriction_error1.total_use, 100)
        self.assertEqual(restriction_error1.item_use, 100)
        restriction_error2 = self.get_restriction_error(fit, item2, Restriction.powergrid)
        self.assertIsNone(restriction_error2)
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass(self):
        # When total consumption is less than output,
        # no errors should be raised
        fit = Fit()
        eve_type = self.ch.type(attributes={Attribute.power: 0})
        item1 = ModuleHigh(eve_type.id, state=State.online)
        item1.attributes = {Attribute.power: 25}
        self.add_item(item1)
        item2 = ModuleHigh(eve_type.id, state=State.online)
        item2.attributes = {Attribute.power: 20}
        self.add_item(item2)
        fit.stats.powergrid.used = 45
        fit.stats.powergrid.output = 50
        restriction_error1 = self.get_restriction_error(fit, item1, Restriction.powergrid)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(fit, item2, Restriction.powergrid)
        self.assertIsNone(restriction_error2)
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_no_attr_eve_type(self):
        # When added item's eve type doesn't have attribute, item
        # shouldn't be tracked by register, and thus, no errors
        # should be raised
        fit = Fit()
        eve_type = self.ch.type()
        item = ModuleHigh(eve_type.id, state=State.online)
        item.attributes = {Attribute.power: 100}
        self.add_item(item)
        fit.stats.powergrid.used = 100
        fit.stats.powergrid.output = 50
        restriction_error = self.get_restriction_error(fit, item, Restriction.powergrid)
        self.assertIsNone(restriction_error)
        self.remove_item(item)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_state(self):
        # When item isn't online, it shouldn't consume anything
        fit = Fit()
        eve_type = self.ch.type(attributes={Attribute.power: 0})
        item = ModuleHigh(eve_type.id, state=State.offline)
        item.attributes = {Attribute.power: 50}
        self.add_item(item)
        fit.stats.powergrid.used = 50
        fit.stats.powergrid.output = 40
        restriction_error = self.get_restriction_error(fit, item, Restriction.powergrid)
        self.assertIsNone(restriction_error)
        self.remove_item(item)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
