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


from eos import ModuleLow
from eos import Restriction
from eos import Ship
from eos.const.eve import AttrId
from tests.integration.restriction.testcase import RestrictionTestCase


class TestLowSlot(RestrictionTestCase):
    """Check functionality of low slot quantity restriction."""

    def setUp(self):
        RestrictionTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.low_slots)

    def test_fail_single(self):
        # Check that error is raised when quantity of used slots exceeds slot
        # quantity provided by ship
        self.fit.ship = Ship(self.mktype(attrs={AttrId.low_slots: 0}).id)
        item = ModuleLow(self.mktype().id)
        self.fit.modules.low.append(item)
        # Action
        error = self.get_error(item, Restriction.low_slot)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.used, 1)
        self.assertEqual(error.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_multiple(self):
        # Check that error works for multiple items, and raised only for those
        # which lie out of bounds
        self.fit.ship = Ship(self.mktype(attrs={AttrId.low_slots: 1}).id)
        item_type = self.mktype()
        item1 = ModuleLow(item_type.id)
        item2 = ModuleLow(item_type.id)
        self.fit.modules.low.append(item1)
        self.fit.modules.low.append(item2)
        # Action
        error1 = self.get_error(item1, Restriction.low_slot)
        # Verification
        self.assertIsNone(error1)
        # Action
        error2 = self.get_error(item2, Restriction.low_slot)
        # Verification
        self.assertIsNotNone(error2)
        self.assertEqual(error2.used, 2)
        self.assertEqual(error2.total, 1)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_multiple_with_nones(self):
        # Make sure Nones are processed properly
        self.fit.ship = Ship(self.mktype(attrs={AttrId.low_slots: 3}).id)
        item_type = self.mktype()
        item1 = ModuleLow(item_type.id)
        item2 = ModuleLow(item_type.id)
        item3 = ModuleLow(item_type.id)
        self.fit.modules.low.place(1, item1)
        self.fit.modules.low.place(4, item2)
        self.fit.modules.low.place(6, item3)
        # Action
        error1 = self.get_error(item1, Restriction.low_slot)
        # Verification
        self.assertIsNone(error1)
        # Action
        error2 = self.get_error(item2, Restriction.low_slot)
        # Verification
        self.assertIsNotNone(error2)
        self.assertEqual(error2.used, 7)
        self.assertEqual(error2.total, 3)
        # Action
        error3 = self.get_error(item2, Restriction.low_slot)
        # Verification
        self.assertIsNotNone(error3)
        self.assertEqual(error3.used, 7)
        self.assertEqual(error3.total, 3)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_item_not_loaded(self):
        # Item still counts even when it's not loaded
        self.fit.ship = Ship(self.mktype(attrs={AttrId.low_slots: 0}).id)
        item = ModuleLow(self.allocate_type_id())
        self.fit.modules.low.append(item)
        # Action
        error = self.get_error(item, Restriction.low_slot)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.used, 1)
        self.assertEqual(error.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_ship_absent(self):
        # When stats module does not specify total slot quantity, make sure it's
        # assumed to be 0
        item = ModuleLow(self.mktype().id)
        self.fit.modules.low.append(item)
        # Action
        error = self.get_error(item, Restriction.low_slot)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.used, 1)
        self.assertEqual(error.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_ship_attr_absent(self):
        self.fit.ship = Ship(self.mktype().id)
        item = ModuleLow(self.mktype().id)
        self.fit.modules.low.append(item)
        # Action
        error = self.get_error(item, Restriction.low_slot)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.used, 1)
        self.assertEqual(error.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_ship_not_loaded(self):
        self.fit.ship = Ship(self.allocate_type_id())
        item = ModuleLow(self.mktype().id)
        self.fit.modules.low.append(item)
        # Action
        error = self.get_error(item, Restriction.low_slot)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.used, 1)
        self.assertEqual(error.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_equal(self):
        self.fit.ship = Ship(self.mktype(attrs={AttrId.low_slots: 2}).id)
        item_type = self.mktype()
        item1 = ModuleLow(item_type.id)
        item2 = ModuleLow(item_type.id)
        self.fit.modules.low.append(item1)
        self.fit.modules.low.append(item2)
        # Action
        error1 = self.get_error(item1, Restriction.low_slot)
        # Verification
        self.assertIsNone(error1)
        # Action
        error2 = self.get_error(item2, Restriction.low_slot)
        # Verification
        self.assertIsNone(error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_greater(self):
        self.fit.ship = Ship(self.mktype(attrs={AttrId.low_slots: 5}).id)
        item_type = self.mktype()
        item1 = ModuleLow(item_type.id)
        item2 = ModuleLow(item_type.id)
        self.fit.modules.low.append(item1)
        self.fit.modules.low.append(item2)
        # Action
        error1 = self.get_error(item1, Restriction.low_slot)
        # Verification
        self.assertIsNone(error1)
        # Action
        error2 = self.get_error(item2, Restriction.low_slot)
        # Verification
        self.assertIsNone(error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_source_none(self):
        # Error shouldn't be raised when fit has no source
        self.fit.ship = Ship(self.mktype(attrs={AttrId.low_slots: 0}).id)
        item = ModuleLow(self.mktype().id)
        self.fit.modules.low.append(item)
        self.fit.source = None
        # Action
        error = self.get_error(item, Restriction.low_slot)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
