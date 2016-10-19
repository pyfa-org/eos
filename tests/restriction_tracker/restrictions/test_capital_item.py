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


class TestCapitalItem(RestrictionTestCase):
    """Check functionality of capital-sized modules restriction"""

    def test_fail_no_ship(self):
        # Check that error is raised on attempt
        # to add capital item to fit w/o ship
        item = self.ch.type_(type_id=1, attributes={Attribute.volume: 4000})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.capital_item)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.subcap_volume_upto, 4000)
        self.assertEqual(restriction_error.holder_volume, 4000)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_subcap(self):
        # Check that error is raised on attempt to add
        # capital item to fit with subcapital ship
        item = self.ch.type_(type_id=1, attributes={Attribute.volume: 4000})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        ship_item = self.ch.type_(type_id=2)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        restriction_error = self.get_restriction_error(holder, Restriction.capital_item)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.subcap_volume_upto, 4000)
        self.assertEqual(restriction_error.holder_volume, 4000)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_subcap_capattr_zero(self):
        # Make sure that mere presence of isCapital attr
        # on a ship (with zero value) doesn't make it capital
        item = self.ch.type_(type_id=1, attributes={Attribute.volume: 4000})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        ship_item = self.ch.type_(type_id=2, attributes={Attribute.is_capital_size: 0.0})
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        restriction_error = self.get_restriction_error(holder, Restriction.capital_item)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.subcap_volume_upto, 4000)
        self.assertEqual(restriction_error.holder_volume, 4000)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_subcap_capattr_value_none(self):
        # Check that error is raised when ship has isCapitalShip
        # attribute, but its value is None
        item = self.ch.type_(type_id=1, attributes={Attribute.volume: 4000})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        ship_item = self.ch.type_(type_id=2, attributes={Attribute.is_capital_size: None})
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        restriction_error = self.get_restriction_error(holder, Restriction.capital_item)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.subcap_volume_upto, 4000)
        self.assertEqual(restriction_error.holder_volume, 4000)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_subcap_capattr_original(self):
        # Make sure that original value of is-capital
        # attribute is used for check
        item = self.ch.type_(type_id=1, attributes={Attribute.volume: 4000})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        ship_item = self.ch.type_(type_id=2, attributes={Attribute.is_capital_size: 0})
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        ship_holder.attributes = {Attribute.is_capital_size: 1.0}
        self.set_ship(ship_holder)
        restriction_error = self.get_restriction_error(holder, Restriction.capital_item)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.subcap_volume_upto, 4000)
        self.assertEqual(restriction_error.holder_volume, 4000)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_subcap_volume_original(self):
        # Make sure original volume value is taken
        item = self.ch.type_(type_id=1, attributes={Attribute.volume: 4000})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        # Set volume below 4000 to check that even when
        # modified attributes are available, raw attributes
        # are taken
        holder.attributes = {Attribute.volume: 100}
        self.track_holder(holder)
        ship_item = self.ch.type_(type_id=2)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        restriction_error = self.get_restriction_error(holder, Restriction.capital_item)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.subcap_volume_upto, 4000)
        self.assertEqual(restriction_error.holder_volume, 4000)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_subcap_volume_subcap(self):
        # Make sure no error raised when non-capital
        # item is added to fit
        item = self.ch.type_(type_id=1, attributes={Attribute.volume: 3999})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.capital_item)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_subcap_holder_other_domain(self):
        # Check that non-ship holders are not affected
        # by restriction
        item = self.ch.type_(type_id=1, attributes={Attribute.volume: 4000})
        holder = Mock(state=State.offline, item=item, _domain=None, spec_set=Ship(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.capital_item)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_subcap_volume_not_specified(self):
        # Check that items with no volume attribute are not restricted
        item = self.ch.type_(type_id=1)
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        ship_item = self.ch.type_(type_id=2)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        restriction_error = self.get_restriction_error(holder, Restriction.capital_item)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_capital(self):
        # Check that capital holders can be added to capital ship
        item = self.ch.type_(type_id=1, attributes={Attribute.volume: 4000})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        ship_item = self.ch.type_(type_id=2, attributes={Attribute.is_capital_size: 1.0})
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        restriction_error = self.get_restriction_error(holder, Restriction.capital_item)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_capital_capattr_value_not_one(self):
        # Check that when non-zero isCapital attr is on a ship,
        # it's considered as capital
        item = self.ch.type_(type_id=1, attributes={Attribute.volume: 4000})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        ship_item = self.ch.type_(type_id=2, attributes={Attribute.is_capital_size: -0.00001})
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        restriction_error = self.get_restriction_error(holder, Restriction.capital_item)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()
