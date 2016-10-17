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
from eos.fit.holder.item import Rig, Ship
from tests.restriction_tracker.restriction_testcase import RestrictionTestCase


class TestRigSize(RestrictionTestCase):
    """Check functionality of rig size restriction"""

    def test_fail_mismatch(self):
        # Error should be raised when mismatching rig size
        # is added to ship
        item = self.ch.type_(type_id=1, attributes={Attribute.rig_size: 10})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=Rig(1))
        self.track_holder(holder)
        ship_item = self.ch.type_(type_id=2, attributes={Attribute.rig_size: 6})
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        restriction_error = self.get_restriction_error(holder, Restriction.rig_size)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.allowed_size, 6)
        self.assertEqual(restriction_error.holder_size, 10)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_original(self):
        # Original value must be taken
        item = self.ch.type_(type_id=1, attributes={Attribute.rig_size: 10})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=Rig(1))
        holder.attributes = {Attribute.rig_size: 5}
        self.track_holder(holder)
        ship_item = self.ch.type_(type_id=2, attributes={Attribute.rig_size: 6})
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        ship_holder.attributes = {Attribute.rig_size: 5}
        self.set_ship(ship_holder)
        restriction_error = self.get_restriction_error(holder, Restriction.rig_size)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.allowed_size, 6)
        self.assertEqual(restriction_error.holder_size, 10)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_no_ship(self):
        # When no ship is assigned, no restriction
        # should be applied to ships
        item = self.ch.type_(type_id=1, attributes={Attribute.rig_size: 10})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=Rig(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.rig_size)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_ship_no_attr(self):
        # If ship doesn't have rig size attribute,
        # no restriction is applied onto rigs
        item = self.ch.type_(type_id=1, attributes={Attribute.rig_size: 10})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=Rig(1))
        self.track_holder(holder)
        ship_item = self.ch.type_(type_id=2)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        ship_holder.attributes = {}
        self.set_ship(ship_holder)
        restriction_error = self.get_restriction_error(holder, Restriction.rig_size)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()
