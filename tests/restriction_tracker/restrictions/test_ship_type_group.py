# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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


from unittest.mock import Mock

from eos.const.eos import Domain, Restriction, State
from eos.const.eve import Attribute
from eos.fit.holder.item import ModuleHigh, Ship
from tests.restriction_tracker.restriction_testcase import RestrictionTestCase


class TestShipTypeGroup(RestrictionTestCase):
    """Check functionality of 'can fit to ship type/group' restriction"""

    def test_fail_type1(self):
        # Check that first type-restriction attribute affects
        # holder
        ship_item = self.ch.type_(type_id=772, group=31)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=1, attributes={Attribute.can_fit_ship_type_1: 10})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.ship_type_group)
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_types, (10,))
        self.assertCountEqual(restriction_error.allowed_groups, ())
        self.assertEqual(restriction_error.ship_type, 772)
        self.assertEqual(restriction_error.ship_group, 31)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_type2(self):
        # Check that second type-restriction attribute affects
        # holder
        ship_item = self.ch.type_(type_id=772, group=31)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=1, attributes={Attribute.can_fit_ship_type_2: 10})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.ship_type_group)
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_types, (10,))
        self.assertCountEqual(restriction_error.allowed_groups, ())
        self.assertEqual(restriction_error.ship_type, 772)
        self.assertEqual(restriction_error.ship_group, 31)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_type3(self):
        # Check that third type-restriction attribute affects
        # holder
        ship_item = self.ch.type_(type_id=772, group=31)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=1, attributes={Attribute.can_fit_ship_type_3: 10})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.ship_type_group)
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_types, (10,))
        self.assertCountEqual(restriction_error.allowed_groups, ())
        self.assertEqual(restriction_error.ship_type, 772)
        self.assertEqual(restriction_error.ship_group, 31)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_type4(self):
        # Check that fourth type-restriction attribute affects
        # holder
        ship_item = self.ch.type_(type_id=772, group=31)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=1, attributes={Attribute.can_fit_ship_type_4: 10})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.ship_type_group)
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_types, (10,))
        self.assertCountEqual(restriction_error.allowed_groups, ())
        self.assertEqual(restriction_error.ship_type, 772)
        self.assertEqual(restriction_error.ship_group, 31)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_type5(self):
        # Check that fifth type-restriction attribute affects
        # holder
        ship_item = self.ch.type_(type_id=772, group=31)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=1, attributes={Attribute.fits_to_shiptype: 10})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.ship_type_group)
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_types, (10,))
        self.assertCountEqual(restriction_error.allowed_groups, ())
        self.assertEqual(restriction_error.ship_type, 772)
        self.assertEqual(restriction_error.ship_group, 31)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_type_multiple_different(self):
        ship_item = self.ch.type_(type_id=772, group=31)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=1, attributes={Attribute.can_fit_ship_type_1: 10,
                                                    Attribute.can_fit_ship_type_2: 11})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.ship_type_group)
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_types, (10, 11))
        self.assertCountEqual(restriction_error.allowed_groups, ())
        self.assertEqual(restriction_error.ship_type, 772)
        self.assertEqual(restriction_error.ship_group, 31)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_type_multiple_same(self):
        ship_item = self.ch.type_(type_id=772, group=31)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=1, attributes={Attribute.can_fit_ship_type_1: 10,
                                                    Attribute.can_fit_ship_type_2: 10})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.ship_type_group)
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_types, (10,))
        self.assertCountEqual(restriction_error.allowed_groups, ())
        self.assertEqual(restriction_error.ship_type, 772)
        self.assertEqual(restriction_error.ship_group, 31)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_group1(self):
        # Check that first group-restriction attribute affects
        # holder
        ship_item = self.ch.type_(type_id=772, group=31)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=1, attributes={Attribute.can_fit_ship_group_1: 38})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.ship_type_group)
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_types, ())
        self.assertCountEqual(restriction_error.allowed_groups, (38,))
        self.assertEqual(restriction_error.ship_type, 772)
        self.assertEqual(restriction_error.ship_group, 31)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_group2(self):
        # Check that second group-restriction attribute affects
        # holder
        ship_item = self.ch.type_(type_id=772, group=31)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=1, attributes={Attribute.can_fit_ship_group_2: 38})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.ship_type_group)
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_types, ())
        self.assertCountEqual(restriction_error.allowed_groups, (38,))
        self.assertEqual(restriction_error.ship_type, 772)
        self.assertEqual(restriction_error.ship_group, 31)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_group3(self):
        # Check that third group-restriction attribute affects
        # holder
        ship_item = self.ch.type_(type_id=772, group=31)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=1, attributes={Attribute.can_fit_ship_group_3: 38})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.ship_type_group)
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_types, ())
        self.assertCountEqual(restriction_error.allowed_groups, (38,))
        self.assertEqual(restriction_error.ship_type, 772)
        self.assertEqual(restriction_error.ship_group, 31)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_group4(self):
        # Check that fourth group-restriction attribute affects
        # holder
        ship_item = self.ch.type_(type_id=772, group=31)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=1, attributes={Attribute.can_fit_ship_group_4: 38})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.ship_type_group)
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_types, ())
        self.assertCountEqual(restriction_error.allowed_groups, (38,))
        self.assertEqual(restriction_error.ship_type, 772)
        self.assertEqual(restriction_error.ship_group, 31)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_group5(self):
        # Check that fourth group-restriction attribute affects
        # holder
        ship_item = self.ch.type_(type_id=772, group=31)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=1, attributes={Attribute.can_fit_ship_group_5: 38})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.ship_type_group)
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_types, ())
        self.assertCountEqual(restriction_error.allowed_groups, (38,))
        self.assertEqual(restriction_error.ship_type, 772)
        self.assertEqual(restriction_error.ship_group, 31)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_group6(self):
        # Check that fourth group-restriction attribute affects
        # holder
        ship_item = self.ch.type_(type_id=772, group=31)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=1, attributes={Attribute.can_fit_ship_group_6: 38})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.ship_type_group)
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_types, ())
        self.assertCountEqual(restriction_error.allowed_groups, (38,))
        self.assertEqual(restriction_error.ship_type, 772)
        self.assertEqual(restriction_error.ship_group, 31)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_group7(self):
        # Check that fourth group-restriction attribute affects
        # holder
        ship_item = self.ch.type_(type_id=772, group=31)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=1, attributes={Attribute.can_fit_ship_group_7: 38})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.ship_type_group)
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_types, ())
        self.assertCountEqual(restriction_error.allowed_groups, (38,))
        self.assertEqual(restriction_error.ship_type, 772)
        self.assertEqual(restriction_error.ship_group, 31)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_group8(self):
        # Check that fourth group-restriction attribute affects
        # holder
        ship_item = self.ch.type_(type_id=772, group=31)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=1, attributes={Attribute.can_fit_ship_group_8: 38})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.ship_type_group)
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_types, ())
        self.assertCountEqual(restriction_error.allowed_groups, (38,))
        self.assertEqual(restriction_error.ship_type, 772)
        self.assertEqual(restriction_error.ship_group, 31)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_group_multiple_different(self):
        ship_item = self.ch.type_(type_id=772, group=31)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=1, attributes={Attribute.can_fit_ship_group_1: 38,
                                                    Attribute.can_fit_ship_group_2: 83})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.ship_type_group)
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_types, ())
        self.assertCountEqual(restriction_error.allowed_groups, (38, 83))
        self.assertEqual(restriction_error.ship_type, 772)
        self.assertEqual(restriction_error.ship_group, 31)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_group_multiple_same(self):
        ship_item = self.ch.type_(type_id=772, group=31)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=1, attributes={Attribute.can_fit_ship_group_1: 38,
                                                    Attribute.can_fit_ship_group_2: 38})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.ship_type_group)
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_types, ())
        self.assertCountEqual(restriction_error.allowed_groups, (38,))
        self.assertEqual(restriction_error.ship_type, 772)
        self.assertEqual(restriction_error.ship_group, 31)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_combined(self):
        # Check that failure is appropriately generated when
        # holder specifies both type and group restrictions
        ship_item = self.ch.type_(type_id=772, group=31)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=1, attributes={Attribute.can_fit_ship_type_1: 1089,
                                                    Attribute.can_fit_ship_group_1: 23})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.ship_type_group)
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_types, (1089,))
        self.assertCountEqual(restriction_error.allowed_groups, (23,))
        self.assertEqual(restriction_error.ship_type, 772)
        self.assertEqual(restriction_error.ship_group, 31)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_no_ship(self):
        # Absent ship should trigger this error too
        item = self.ch.type_(type_id=1, attributes={Attribute.can_fit_ship_type_1: 10})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.ship_type_group)
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_types, (10,))
        self.assertCountEqual(restriction_error.allowed_groups, ())
        self.assertEqual(restriction_error.ship_type, None)
        self.assertEqual(restriction_error.ship_group, None)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_attr_original(self):
        # Make sure original value is taken
        ship_item = self.ch.type_(type_id=772, group=31)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=1, attributes={Attribute.can_fit_ship_type_1: 10})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder.attributes = {Attribute.can_fit_ship_type_1: 772}
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.ship_type_group)
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error.allowed_types, (10,))
        self.assertCountEqual(restriction_error.allowed_groups, ())
        self.assertEqual(restriction_error.ship_type, 772)
        self.assertEqual(restriction_error.ship_group, 31)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_type_match(self):
        # When type of ship matches type-restriction attribute,
        # no error should be raised
        ship_item = self.ch.type_(type_id=554, group=23)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=1, attributes={Attribute.can_fit_ship_type_1: 554})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.ship_type_group)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_group_match(self):
        # When type of ship matches group-restriction attribute,
        # no error should be raised
        ship_item = self.ch.type_(type_id=554, group=23)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=1, attributes={Attribute.can_fit_ship_group_1: 23})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.ship_type_group)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_combined_type_match(self):
        # Check that it's enough to match type condition
        # to be fittable, even if both conditions are specified
        ship_item = self.ch.type_(type_id=671, group=31)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=1, attributes={Attribute.can_fit_ship_type_1: 671,
                                                    Attribute.can_fit_ship_group_1: 38})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.ship_type_group)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_combined_group_atch(self):
        # Check that it's enough to match group condition
        # to be fittable, even if both conditions are specified
        ship_item = self.ch.type_(type_id=554, group=23)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=1, attributes={Attribute.can_fit_ship_type_1: 1089,
                                                    Attribute.can_fit_ship_group_1: 23})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.ship_type_group)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_non_ship_holder(self):
        # Holders not belonging to ship shouldn't be affected
        ship_item = self.ch.type_(type_id=772, group=31)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=1, attributes={Attribute.can_fit_ship_type_1: 10})
        holder = Mock(state=State.offline, item=item, _domain=None, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.ship_type_group)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()
