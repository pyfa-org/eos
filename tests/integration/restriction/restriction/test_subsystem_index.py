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


from eos import ModuleHigh
from eos import Restriction
from eos import Subsystem
from eos.const.eve import AttrId
from tests.integration.restriction.testcase import RestrictionTestCase


class TestSubsystemIndex(RestrictionTestCase):
    """Check functionality of subsystem slot index restriction."""

    def setUp(self):
        RestrictionTestCase.setUp(self)
        self.index_attr = self.mkattr(attr_id=AttrId.subsystem_slot)

    def test_fail(self):
        # Check that if 2 or more items are put into single slot index, error is
        # raised
        item_type = self.mktype(attrs={self.index_attr.id: 120})
        item1 = Subsystem(item_type.id)
        item2 = Subsystem(item_type.id)
        self.fit.subsystems.add(item1)
        self.fit.subsystems.add(item2)
        # Action
        error1 = self.get_error(item1, Restriction.subsystem_index)
        self.assertIsNotNone(error1)
        self.assertEqual(error1.slot_index, 120)
        # Action
        error2 = self.get_error(item2, Restriction.subsystem_index)
        self.assertIsNotNone(error2)
        self.assertEqual(error2.slot_index, 120)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_fail_item_class_other(self):
        # Make sure items of all classes are affected
        item_type = self.mktype(attrs={self.index_attr.id: 120})
        item1 = ModuleHigh(item_type.id)
        item2 = ModuleHigh(item_type.id)
        self.fit.modules.high.append(item1)
        self.fit.modules.high.append(item2)
        # Action
        error1 = self.get_error(item1, Restriction.subsystem_index)
        # Verification
        self.assertIsNotNone(error1)
        self.assertEqual(error1.slot_index, 120)
        # Action
        error2 = self.get_error(item2, Restriction.subsystem_index)
        # Verification
        self.assertIsNotNone(error2)
        self.assertEqual(error2.slot_index, 120)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_pass(self):
        # Single item which takes some slot shouldn't trigger any errors
        item = Subsystem(self.mktype(attrs={self.index_attr.id: 120}).id)
        self.fit.subsystems.add(item)
        # Action
        error = self.get_error(item, Restriction.subsystem_index)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_pass_slots_different(self):
        # Items taking different slots shouldn't trigger any errors
        item1 = Subsystem(self.mktype(attrs={self.index_attr.id: 120}).id)
        item2 = Subsystem(self.mktype(attrs={self.index_attr.id: 121}).id)
        self.fit.subsystems.add(item1)
        self.fit.subsystems.add(item2)
        # Action
        error1 = self.get_error(item1, Restriction.subsystem_index)
        # Verification
        self.assertIsNone(error1)
        # Action
        error2 = self.get_error(item2, Restriction.subsystem_index)
        # Verification
        self.assertIsNone(error2)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_pass_items_not_loaded(self):
        item_type_id = self.allocate_type_id()
        item1 = Subsystem(item_type_id)
        item2 = Subsystem(item_type_id)
        self.fit.subsystems.add(item1)
        self.fit.subsystems.add(item2)
        # Action
        error1 = self.get_error(item1, Restriction.subsystem_index)
        self.assertIsNone(error1)
        # Action
        error2 = self.get_error(item2, Restriction.subsystem_index)
        self.assertIsNone(error2)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)
