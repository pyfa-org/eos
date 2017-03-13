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
from eos.const.eos import Restriction, State
from eos.const.eve import Attribute
from tests.integration.restriction.restriction_testcase import RestrictionTestCase


class TestCapitalItem(RestrictionTestCase):
    """Check functionality of capital-sized modules restriction"""

    def test_fail_no_ship(self):
        # Check that error is raised on attempt
        # to add capital item to fit w/o ship
        fit = Fit()
        eve_type = self.ch.type(attributes={Attribute.volume: 3501})
        item = ModuleHigh(eve_type.id, state=State.offline)
        self.add_item(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.capital_item)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.max_subcap_volume, 3500)
        self.assertEqual(restriction_error.item_volume, 3501)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_fail_subcap(self):
        fit = Fit()
        eve_type = self.ch.type(attributes={Attribute.volume: 3501})
        item = ModuleHigh(eve_type.id, state=State.offline)
        self.add_item(item)
        ship_eve_type = self.ch.type()
        ship_item = Ship(ship_eve_type.id)
        fit.ship = ship_item
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.capital_item)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.max_subcap_volume, 3500)
        self.assertEqual(restriction_error.item_volume, 3501)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_fail_subcap_capattr_zero(self):
        # Make sure that mere presence of isCapital attr
        # on a ship (with zero value) doesn't make it capital
        fit = Fit()
        eve_type = self.ch.type(attributes={Attribute.volume: 3501})
        item = ModuleHigh(eve_type.id, state=State.offline)
        self.add_item(item)
        ship_eve_type = self.ch.type(attributes={Attribute.is_capital_size: 0.0})
        ship_item = Ship(ship_eve_type.id)
        fit.ship = ship_item
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.capital_item)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.max_subcap_volume, 3500)
        self.assertEqual(restriction_error.item_volume, 3501)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_fail_subcap_capattr_value_none(self):
        # Check that error is raised when ship has isCapitalShip
        # attribute, but its value is None
        fit = Fit()
        eve_type = self.ch.type(attributes={Attribute.volume: 3501})
        item = ModuleHigh(eve_type.id, state=State.offline)
        self.add_item(item)
        ship_eve_type = self.ch.type(attributes={Attribute.is_capital_size: None})
        ship_item = Ship(ship_eve_type.id)
        fit.ship = ship_item
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.capital_item)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.max_subcap_volume, 3500)
        self.assertEqual(restriction_error.item_volume, 3501)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_fail_subcap_capattr_eve_type(self):
        # Make sure that eve type value of is-capital
        # attribute is used for check
        fit = Fit()
        eve_type = self.ch.type(attributes={Attribute.volume: 3501})
        item = ModuleHigh(eve_type.id, state=State.offline)
        self.add_item(item)
        ship_eve_type = self.ch.type(attributes={Attribute.is_capital_size: 0})
        ship_item = Ship(ship_eve_type.id)
        ship_item.attributes = {Attribute.is_capital_size: 1.0}
        fit.ship = ship_item
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.capital_item)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.max_subcap_volume, 3500)
        self.assertEqual(restriction_error.item_volume, 3501)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_fail_subcap_volume_eve_type(self):
        # Make sure eve type volume value is taken
        fit = Fit()
        eve_type = self.ch.type(attributes={Attribute.volume: 3501})
        item = ModuleHigh(eve_type.id, state=State.offline)
        # Set volume below 3500 to check that even when
        # modified attributes are available, raw attributes
        # are taken
        item.attributes = {Attribute.volume: 100}
        self.add_item(item)
        ship_eve_type = self.ch.type()
        ship_item = Ship(ship_eve_type.id)
        fit.ship = ship_item
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.capital_item)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.max_subcap_volume, 3500)
        self.assertEqual(restriction_error.item_volume, 3501)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_subcap_volume_subcap(self):
        # Make sure no error raised when non-capital
        # item is added to fit
        fit = Fit()
        eve_type = self.ch.type(attributes={Attribute.volume: 3500})
        item = ModuleHigh(eve_type.id, state=State.offline)
        self.add_item(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.capital_item)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_subcap_volume_not_specified(self):
        # Check that items with no volume attribute
        # on eve type are not restricted
        fit = Fit()
        eve_type = self.ch.type()
        item = ModuleHigh(eve_type.id, state=State.offline)
        self.add_item(item)
        ship_eve_type = self.ch.type()
        ship_item = Ship(ship_eve_type.id)
        fit.ship = ship_item
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.capital_item)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_capital(self):
        # Check that capital items can be added to capital ship
        fit = Fit()
        eve_type = self.ch.type(attributes={Attribute.volume: 3501})
        item = ModuleHigh(eve_type.id, state=State.offline)
        self.add_item(item)
        ship_eve_type = self.ch.type(attributes={Attribute.is_capital_size: 1.0})
        ship_item = Ship(ship_eve_type.id)
        fit.ship = ship_item
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.capital_item)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_capital_capattr_value_not_one(self):
        # Check that when non-zero isCapital attr is on a ship,
        # it's considered as capital
        fit = Fit()
        eve_type = self.ch.type(attributes={Attribute.volume: 3501})
        item = ModuleHigh(eve_type.id, state=State.offline)
        self.add_item(item)
        ship_eve_type = self.ch.type(attributes={Attribute.is_capital_size: -0.00001})
        ship_item = Ship(ship_eve_type.id)
        fit.ship = ship_item
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.capital_item)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_item_other_class(self):
        fit = Fit()
        eve_type = self.ch.type(attributes={Attribute.volume: 3501})
        item = Rig(eve_type.id, state=State.offline)
        self.add_item(item)
        ship_eve_type = self.ch.type()
        ship_item = Ship(ship_eve_type.id)
        fit.ship = ship_item
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.capital_item)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
