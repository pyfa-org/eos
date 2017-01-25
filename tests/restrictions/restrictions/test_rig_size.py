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


from eos.const.eos import Restriction
from eos.const.eve import Attribute
from eos.fit.item import Rig, Ship
from tests.restrictions.restriction_testcase import RestrictionTestCase


class TestRigSize(RestrictionTestCase):
    """Check functionality of rig size restriction"""

    def test_fail_mismatch(self):
        # Error should be raised when mismatching rig size
        # is added to ship
        eve_type = self.ch.type_(type_id=1, attributes={Attribute.rig_size: 10})
        holder = self.make_item_mock(Rig, eve_type)
        self.add_holder(holder)
        ship_eve_type = self.ch.type_(type_id=2, attributes={Attribute.rig_size: 6})
        ship_holder = self.make_item_mock(Ship, ship_eve_type)
        self.set_ship(ship_holder)
        restriction_error = self.get_restriction_error(holder, Restriction.rig_size)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.allowed_size, 6)
        self.assertEqual(restriction_error.holder_size, 10)
        self.remove_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_attr_eve_type(self):
        # EVE type value must be taken
        eve_type = self.ch.type_(type_id=1, attributes={Attribute.rig_size: 10})
        holder = self.make_item_mock(Rig, eve_type)
        holder.attributes = {Attribute.rig_size: 5}
        self.add_holder(holder)
        ship_eve_type = self.ch.type_(type_id=2, attributes={Attribute.rig_size: 6})
        ship_holder = self.make_item_mock(Ship, ship_eve_type)
        ship_holder.attributes = {Attribute.rig_size: 5}
        self.set_ship(ship_holder)
        restriction_error = self.get_restriction_error(holder, Restriction.rig_size)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.allowed_size, 6)
        self.assertEqual(restriction_error.holder_size, 10)
        self.remove_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_no_ship(self):
        # When no ship is assigned, no restriction
        # should be applied to ships
        eve_type = self.ch.type_(type_id=1, attributes={Attribute.rig_size: 10})
        holder = self.make_item_mock(Rig, eve_type)
        self.add_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.rig_size)
        self.assertIsNone(restriction_error)
        self.remove_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_ship_no_attr(self):
        # If ship doesn't have rig size attribute,
        # no restriction is applied onto rigs
        eve_type = self.ch.type_(type_id=1, attributes={Attribute.rig_size: 10})
        holder = self.make_item_mock(Rig, eve_type)
        self.add_holder(holder)
        ship_eve_type = self.ch.type_(type_id=2)
        ship_holder = self.make_item_mock(Ship, ship_eve_type)
        ship_holder.attributes = {}
        self.set_ship(ship_holder)
        restriction_error = self.get_restriction_error(holder, Restriction.rig_size)
        self.assertIsNone(restriction_error)
        self.remove_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()
