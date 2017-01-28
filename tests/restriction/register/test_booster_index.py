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


from eos.const.eos import Restriction, State
from eos.const.eve import Attribute
from eos.fit.item import Booster, ModuleHigh
from tests.restriction.restriction_testcase import RestrictionTestCase


class TestBoosterIndex(RestrictionTestCase):
    """Check functionality of booster slot index restriction"""

    def test_fail(self):
        # Check that if 2 or more items are put into single slot
        # index, error is raised
        eve_type = self.ch.type(type_id=1, attributes={Attribute.boosterness: 120})
        item1 = self.make_item_mock(Booster, eve_type)
        item2 = self.make_item_mock(Booster, eve_type)
        self.add_item(item1)
        self.add_item(item2)
        restriction_error1 = self.get_restriction_error(item1, Restriction.booster_index)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.item_slot_index, 120)
        restriction_error2 = self.get_restriction_error(item2, Restriction.booster_index)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.item_slot_index, 120)
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_other_item_class(self):
        # Make sure items of all classes are affected
        eve_type = self.ch.type(type_id=1, attributes={Attribute.boosterness: 120})
        item1 = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        item2 = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        self.add_item(item1)
        self.add_item(item2)
        restriction_error1 = self.get_restriction_error(item1, Restriction.booster_index)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.item_slot_index, 120)
        restriction_error2 = self.get_restriction_error(item2, Restriction.booster_index)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.item_slot_index, 120)
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_attr_eve_type(self):
        # Make sure that eve type attributes are used
        eve_type = self.ch.type(type_id=1, attributes={Attribute.boosterness: 120})
        item1 = self.make_item_mock(Booster, eve_type)
        item2 = self.make_item_mock(Booster, eve_type)
        item1.attributes = {Attribute.boosterness: 119}
        item2.attributes = {Attribute.boosterness: 121}
        self.add_item(item1)
        self.add_item(item2)
        restriction_error1 = self.get_restriction_error(item1, Restriction.booster_index)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.item_slot_index, 120)
        restriction_error2 = self.get_restriction_error(item2, Restriction.booster_index)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.item_slot_index, 120)
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass(self):
        # Single item which takes some slot shouldn't
        # trigger any errors
        eve_type = self.ch.type(type_id=1, attributes={Attribute.boosterness: 120})
        item = self.make_item_mock(Booster, eve_type)
        self.add_item(item)
        restriction_error = self.get_restriction_error(item, Restriction.booster_index)
        self.assertIsNone(restriction_error)
        self.remove_item(item)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_different(self):
        # Items taking different slots shouldn't trigger any errors
        eve_type1 = self.ch.type(type_id=1, attributes={Attribute.boosterness: 120})
        eve_type2 = self.ch.type(type_id=2, attributes={Attribute.boosterness: 121})
        item1 = self.make_item_mock(Booster, eve_type1)
        item2 = self.make_item_mock(Booster, eve_type2)
        self.add_item(item1)
        self.add_item(item2)
        restriction_error1 = self.get_restriction_error(item1, Restriction.booster_index)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(item2, Restriction.booster_index)
        self.assertIsNone(restriction_error2)
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()
