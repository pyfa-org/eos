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


from eos import *
from eos.const.eve import AttributeId
from tests.integration.restriction.restriction_testcase import (
    RestrictionTestCase)


class TestShipTypeGroup(RestrictionTestCase):
    """Check functionality of 'can fit to ship type/group' restriction."""

    def setUp(self):
        super().setUp()
        self.ch.attr(attribute_id=AttributeId.can_fit_ship_type_1)
        self.ch.attr(attribute_id=AttributeId.can_fit_ship_type_2)
        self.ch.attr(attribute_id=AttributeId.can_fit_ship_group_1)
        self.ch.attr(attribute_id=AttributeId.can_fit_ship_group_2)

    def test_fail_type(self):
        ship_eve_type = self.ch.type(group_id=31)
        self.fit.ship = Ship(ship_eve_type.id)
        item = ModuleHigh(self.ch.type(
            attributes={AttributeId.can_fit_ship_type_1: 10}).id)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.ship_type_group)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_types, [10])
        self.assertCountEqual(restriction_error.allowed_groups, ())
        self.assertEqual(restriction_error.ship_type, ship_eve_type.id)
        self.assertEqual(restriction_error.ship_group, 31)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_type_multiple_different(self):
        ship_eve_type = self.ch.type(group_id=31)
        self.fit.ship = Ship(ship_eve_type.id)
        item = ModuleHigh(self.ch.type(attributes={
            AttributeId.can_fit_ship_type_1: 10,
            AttributeId.can_fit_ship_type_2: 11}).id)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.ship_type_group)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_types, (10, 11))
        self.assertCountEqual(restriction_error.allowed_groups, ())
        self.assertEqual(restriction_error.ship_type, ship_eve_type.id)
        self.assertEqual(restriction_error.ship_group, 31)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_type_multiple_same(self):
        ship_eve_type = self.ch.type(group_id=31)
        self.fit.ship = Ship(ship_eve_type.id)
        item = ModuleHigh(self.ch.type(attributes={
            AttributeId.can_fit_ship_type_1: 10,
            AttributeId.can_fit_ship_type_2: 10}).id)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.ship_type_group)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_types, [10])
        self.assertCountEqual(restriction_error.allowed_groups, ())
        self.assertEqual(restriction_error.ship_type, ship_eve_type.id)
        self.assertEqual(restriction_error.ship_group, 31)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_group(self):
        ship_eve_type = self.ch.type(group_id=31)
        self.fit.ship = Ship(ship_eve_type.id)
        item = ModuleHigh(self.ch.type(
            attributes={AttributeId.can_fit_ship_group_1: 38}).id)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.ship_type_group)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_types, ())
        self.assertCountEqual(restriction_error.allowed_groups, [38])
        self.assertEqual(restriction_error.ship_type, ship_eve_type.id)
        self.assertEqual(restriction_error.ship_group, 31)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_group_multiple_different(self):
        ship_eve_type = self.ch.type(group_id=31)
        self.fit.ship = Ship(ship_eve_type.id)
        item = ModuleHigh(self.ch.type(attributes={
            AttributeId.can_fit_ship_group_1: 38,
            AttributeId.can_fit_ship_group_2: 83}).id)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.ship_type_group)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_types, ())
        self.assertCountEqual(restriction_error.allowed_groups, (38, 83))
        self.assertEqual(restriction_error.ship_type, ship_eve_type.id)
        self.assertEqual(restriction_error.ship_group, 31)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_group_multiple_same(self):
        ship_eve_type = self.ch.type(group_id=31)
        self.fit.ship = Ship(ship_eve_type.id)
        item = ModuleHigh(self.ch.type(attributes={
            AttributeId.can_fit_ship_group_1: 38,
            AttributeId.can_fit_ship_group_2: 38}).id)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.ship_type_group)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_types, ())
        self.assertCountEqual(restriction_error.allowed_groups, [38])
        self.assertEqual(restriction_error.ship_type, ship_eve_type.id)
        self.assertEqual(restriction_error.ship_group, 31)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_combined(self):
        # Check that failure is appropriately generated when item specifies both
        # type and group restrictions
        ship_eve_type = self.ch.type(group_id=31)
        self.fit.ship = Ship(ship_eve_type.id)
        item = ModuleHigh(self.ch.type(attributes={
            AttributeId.can_fit_ship_type_1: 1089,
            AttributeId.can_fit_ship_group_1: 23}).id)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.ship_type_group)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_types, [1089])
        self.assertCountEqual(restriction_error.allowed_groups, [23])
        self.assertEqual(restriction_error.ship_type, ship_eve_type.id)
        self.assertEqual(restriction_error.ship_group, 31)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_no_ship(self):
        # Absent ship should trigger this error too
        item = ModuleHigh(self.ch.type(
            attributes={AttributeId.can_fit_ship_type_1: 10}).id)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.ship_type_group)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_types, [10])
        self.assertCountEqual(restriction_error.allowed_groups, ())
        self.assertEqual(restriction_error.ship_type, None)
        self.assertEqual(restriction_error.ship_group, None)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_type_match(self):
        # When type of ship matches type-restriction attribute, no error should
        # be raised
        ship_eve_type = self.ch.type(group_id=23)
        self.fit.ship = Ship(ship_eve_type.id)
        item = ModuleHigh(self.ch.type(
            attributes={AttributeId.can_fit_ship_type_1: ship_eve_type.id}).id)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.ship_type_group)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_group_match(self):
        # When type of ship matches group-restriction attribute, no error should
        # be raised
        self.fit.ship = Ship(self.ch.type(group_id=23).id)
        item = ModuleHigh(self.ch.type(
            attributes={AttributeId.can_fit_ship_group_1: 23}).id)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.ship_type_group)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_combined_type_match(self):
        # Check that it's enough to match type condition to be fittable, even if
        # both conditions are specified
        ship_eve_type = self.ch.type(group_id=31)
        self.fit.ship = Ship(ship_eve_type.id)
        item = ModuleHigh(self.ch.type(attributes={
            AttributeId.can_fit_ship_type_1: ship_eve_type.id,
            AttributeId.can_fit_ship_group_1: 38}).id)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.ship_type_group)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_combined_group_match(self):
        # Check that it's enough to match group condition to be fittable, even
        # if both conditions are specified
        self.fit.ship = Ship(self.ch.type(group_id=23).id)
        item = ModuleHigh(self.ch.type(attributes={
            AttributeId.can_fit_ship_type_1: 1089,
            AttributeId.can_fit_ship_group_1: 23}).id)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.ship_type_group)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_item_other_class(self):
        self.fit.ship = Ship(self.ch.type(group_id=31).id)
        item = Rig(self.ch.type(
            attributes={AttributeId.can_fit_ship_type_1: 10}).id)
        self.fit.rigs.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.ship_type_group)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_no_source(self):
        ship_eve_type = self.ch.type(group_id=31)
        self.fit.ship = Ship(ship_eve_type.id)
        item = ModuleHigh(self.ch.type(
            attributes={AttributeId.can_fit_ship_type_1: 10}).id)
        self.fit.modules.high.append(item)
        self.fit.source = None
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.ship_type_group)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
