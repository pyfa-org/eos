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


from eos import Drone
from eos import Implant
from eos import Restriction
from eos import Ship
from eos.const.eve import AttrId
from tests.integration.restriction.testcase import RestrictionTestCase


class TestDroneGroup(RestrictionTestCase):
    """Check functionality of drone group restriction."""

    def test_fail_group1_mismatch(self):
        # Check that error is returned on attempt to add drone from group
        # mismatching to first restriction attr
        self.fit.ship = Ship(self.mktype(
            attrs={AttrId.allowed_drone_group_1: 4}).id)
        item = Drone(self.mktype(group_id=56).id)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.drone_group)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.group_id, 56)
        self.assertCountEqual(error.allowed_group_ids, [4])
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_group2_mismatch(self):
        # Check that error is returned on attempt to add drone from group
        # mismatching to second restriction attr
        self.fit.ship = Ship(self.mktype(
            attrs={AttrId.allowed_drone_group_2: 69}).id)
        item = Drone(self.mktype(group_id=797).id)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.drone_group)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.group_id, 797)
        self.assertCountEqual(error.allowed_group_ids, [69])
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_group_mismatch_combined(self):
        # Check that error is returned on attempt to add drone from group
        # mismatching to both restriction attributes
        self.fit.ship = Ship(self.mktype(attrs={
            AttrId.allowed_drone_group_1: 48,
            AttrId.allowed_drone_group_2: 106}).id)
        item = Drone(self.mktype(group_id=803).id)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.drone_group)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.group_id, 803)
        self.assertCountEqual(error.allowed_group_ids, [48, 106])
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_drone_group_none(self):
        # Check that drone from None group is subject to restriction
        self.fit.ship = Ship(self.mktype(
            attrs={AttrId.allowed_drone_group_1: 1896}).id)
        item = Drone(self.mktype(group_id=None).id)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.drone_group)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.group_id, None)
        self.assertCountEqual(error.allowed_group_ids, [1896])
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_ship_absent(self):
        # Check that restriction isn't applied when fit doesn't have ship
        item = Drone(self.mktype(group_id=None).id)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.drone_group)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_ship_attr_absent(self):
        # Check that restriction isn't applied when fit has ship, but without
        # restriction attr
        self.fit.ship = Ship(self.mktype().id)
        item = Drone(self.mktype(group_id=71).id)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.drone_group)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_ship_not_loaded(self):
        self.fit.ship = Ship(self.allocate_type_id())
        item = Drone(self.mktype(group_id=56).id)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.drone_group)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_item_not_loaded(self):
        self.fit.ship = Ship(self.mktype(
            attrs={AttrId.allowed_drone_group_1: 1896}).id)
        item = Drone(self.allocate_type_id())
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.drone_group)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_item_class_other(self):
        # Check that restriction is not applied to items which are not drones
        self.fit.ship = Ship(self.mktype(
            attrs={AttrId.allowed_drone_group_1: 4}).id)
        item = Implant(self.mktype(group_id=56).id)
        self.fit.implants.add(item)
        # Action
        error = self.get_error(item, Restriction.drone_group)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_group1_match(self):
        # Check that no error raised when drone of group matching to first
        # restriction attr is added
        self.fit.ship = Ship(self.mktype(
            attrs={AttrId.allowed_drone_group_1: 22}).id)
        item = Drone(self.mktype(group_id=22).id)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.drone_group)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_group2_match(self):
        # Check that no error raised when drone of group matching to second
        # restriction attr is added
        self.fit.ship = Ship(self.mktype(
            attrs={AttrId.allowed_drone_group_2: 67}).id)
        item = Drone(self.mktype(group_id=67).id)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.drone_group)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_group_combination_match(self):
        # Check that no error raised when drone of group matching to any of two
        # restriction attributes is added
        self.fit.ship = Ship(self.mktype(attrs={
            AttrId.allowed_drone_group_1: 907,
            AttrId.allowed_drone_group_2: 53}).id)
        item = Drone(self.mktype(group_id=53).id)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.drone_group)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)
