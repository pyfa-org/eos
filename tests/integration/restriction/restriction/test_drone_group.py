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
from eos.const.eve import Attribute
from tests.integration.restriction.restriction_testcase import RestrictionTestCase


class TestDroneGroup(RestrictionTestCase):
    """Check functionality of drone group restriction"""

    def test_fail_mismatch1(self):
        # Check that error is returned on attempt
        # to add drone from group mismatching to
        # first restriction attribute
        fit = Fit()
        fit.ship = Ship(self.ch.type(attributes={Attribute.allowed_drone_group_1: 4}).id)
        item = Drone(self.ch.type(group=56).id)
        fit.drones.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.drone_group)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_groups, [4])
        self.assertEqual(restriction_error.drone_group, 56)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_fail_mismatch2(self):
        # Check that error is returned on attempt
        # to add drone from group mismatching to
        # second restriction attribute
        fit = Fit()
        fit.ship = Ship(self.ch.type(attributes={Attribute.allowed_drone_group_2: 69}).id)
        item = Drone(self.ch.type(group=797).id)
        fit.drones.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.drone_group)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_groups, [69])
        self.assertEqual(restriction_error.drone_group, 797)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_fail_mismatch_combined(self):
        # Check that error is returned on attempt
        # to add drone from group mismatching to
        # both restriction attributes
        fit = Fit()
        fit.ship = Ship(self.ch.type(
            attributes={Attribute.allowed_drone_group_1: 48, Attribute.allowed_drone_group_2: 106}
        ).id)
        item = Drone(self.ch.type(group=803).id)
        fit.drones.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.drone_group)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_groups, (48, 106))
        self.assertEqual(restriction_error.drone_group, 803)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_fail_drone_none(self):
        # Check that drone from None group is subject
        # to restriction
        fit = Fit()
        fit.ship = Ship(self.ch.type(attributes={Attribute.allowed_drone_group_1: 1896}).id)
        item = Drone(self.ch.type(group=None).id)
        fit.drones.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.drone_group)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_groups, [1896])
        self.assertEqual(restriction_error.drone_group, None)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_no_ship(self):
        # Check that restriction isn't applied
        # when fit doesn't have ship
        fit = Fit()
        item = Drone(self.ch.type(group=None).id)
        fit.drones.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.drone_group)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_ship_no_restriction(self):
        # Check that restriction isn't applied
        # when fit has ship, but without restriction
        # attribute
        fit = Fit()
        fit.ship = Ship(self.ch.type().id)
        item = Drone(self.ch.type(group=71).id)
        fit.drones.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.drone_group)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_non_drone(self):
        # Check that restriction is not applied
        # to items which are not drones
        fit = Fit()
        fit.ship = Ship(self.ch.type(attributes={Attribute.allowed_drone_group_1: 4}).id)
        item = Implant(self.ch.type(group=56).id)
        fit.implants.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.drone_group)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_match1(self):
        # Check that no error raised when drone of group
        # matching to first restriction attribute is added
        fit = Fit()
        fit.ship = Ship(self.ch.type(attributes={Attribute.allowed_drone_group_1: 22}).id)
        item = Drone(self.ch.type(group=22).id)
        fit.drones.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.drone_group)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_match2(self):
        # Check that no error raised when drone of group
        # matching to second restriction attribute is added
        fit = Fit()
        fit.ship = Ship(self.ch.type(attributes={Attribute.allowed_drone_group_2: 67}).id)
        item = Drone(self.ch.type(group=67).id)
        fit.drones.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.drone_group)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_match_combination(self):
        # Check that no error raised when drone of group
        # matching to any of two restriction attributes
        # is added
        fit = Fit()
        fit.ship = Ship(self.ch.type(
            attributes={Attribute.allowed_drone_group_1: 907, Attribute.allowed_drone_group_2: 53}
        ).id)
        item = Drone(self.ch.type(group=53).id)
        fit.drones.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.drone_group)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_no_source(self):
        fit = Fit()
        fit.ship = Ship(self.ch.type(attributes={Attribute.allowed_drone_group_1: 4}).id)
        item = Drone(self.ch.type(group=56).id)
        fit.drones.add(item)
        fit.source = None
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.drone_group)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
