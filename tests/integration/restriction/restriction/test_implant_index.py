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


class TestImplantIndex(RestrictionTestCase):
    """Check functionality of implant slot index restriction"""

    def test_fail(self):
        # Check that if 2 or more items are put into single slot
        # index, error is raised
        fit = Fit()
        eve_type = self.ch.type(attributes={Attribute.implantness: 120})
        item1 = Implant(eve_type.id)
        item2 = Implant(eve_type.id)
        self.add_item(item1)
        self.add_item(item2)
        restriction_error1 = self.get_restriction_error(fit, item1, Restriction.implant_index)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.item_slot_index, 120)
        restriction_error2 = self.get_restriction_error(fit, item2, Restriction.implant_index)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.item_slot_index, 120)
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_fail_other_item_class(self):
        # Make sure items of all classes are affected
        fit = Fit()
        eve_type = self.ch.type(attributes={Attribute.implantness: 120})
        item1 = ModuleHigh(eve_type.id, state=State.offline)
        item2 = ModuleHigh(eve_type.id, state=State.offline)
        self.add_item(item1)
        self.add_item(item2)
        restriction_error1 = self.get_restriction_error(fit, item1, Restriction.implant_index)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.item_slot_index, 120)
        restriction_error2 = self.get_restriction_error(fit, item2, Restriction.implant_index)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.item_slot_index, 120)
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_fail_attr_eve_type(self):
        # Make sure that eve type attributes are used
        fit = Fit()
        eve_type = self.ch.type(attributes={Attribute.implantness: 120})
        item1 = Implant(eve_type.id)
        item2 = Implant(eve_type.id)
        item1.attributes = {Attribute.implantness: 119}
        item2.attributes = {Attribute.implantness: 121}
        self.add_item(item1)
        self.add_item(item2)
        restriction_error1 = self.get_restriction_error(fit, item1, Restriction.implant_index)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.item_slot_index, 120)
        restriction_error2 = self.get_restriction_error(fit, item2, Restriction.implant_index)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.item_slot_index, 120)
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass(self):
        # Single item which takes some slot shouldn't
        # trigger any errors
        fit = Fit()
        eve_type = self.ch.type(attributes={Attribute.implantness: 120})
        item = Implant(eve_type.id)
        self.add_item(item)
        restriction_error = self.get_restriction_error(fit, item, Restriction.implant_index)
        self.assertIsNone(restriction_error)
        self.remove_item(item)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_different(self):
        # Items taking different slots shouldn't trigger any errors
        fit = Fit()
        eve_type1 = self.ch.type(attributes={Attribute.implantness: 120})
        eve_type2 = self.ch.type(attributes={Attribute.implantness: 121})
        item1 = Implant(eve_type1.id)
        item2 = Implant(eve_type2.id)
        self.add_item(item1)
        self.add_item(item2)
        restriction_error1 = self.get_restriction_error(fit, item1, Restriction.implant_index)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(fit, item2, Restriction.implant_index)
        self.assertIsNone(restriction_error2)
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
