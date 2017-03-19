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


class TestCapitalItem(RestrictionTestCase):
    """Check functionality of capital-sized modules restriction"""

    def test_fail_no_ship(self):
        # Check that error is raised on attempt
        # to add capital item to fit w/o ship
        fit = Fit()
        item = ModuleHigh(self.ch.type(attributes={Attribute.volume: 3501}).id, state=State.offline)
        fit.modules.high.append(item)
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
        fit.ship = Ship(self.ch.type().id)
        item = ModuleHigh(self.ch.type(attributes={Attribute.volume: 3501}).id, state=State.offline)
        fit.modules.high.append(item)
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
        fit.ship = Ship(self.ch.type(attributes={Attribute.is_capital_size: 0.0}).id)
        item = ModuleHigh(self.ch.type(attributes={Attribute.volume: 3501}).id, state=State.offline)
        fit.modules.high.append(item)
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
        fit.ship = Ship(self.ch.type(attributes={Attribute.is_capital_size: None}).id)
        item = ModuleHigh(self.ch.type(attributes={Attribute.volume: 3501}).id, state=State.offline)
        fit.modules.high.append(item)
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
        item = ModuleHigh(self.ch.type(attributes={Attribute.volume: 3500}).id, state=State.offline)
        fit.modules.high.append(item)
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
        item = ModuleHigh(self.ch.type().id, state=State.offline)
        fit.modules.high.append(item)
        fit.ship = Ship(self.ch.type().id)
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
        fit.ship = Ship(self.ch.type(attributes={Attribute.is_capital_size: 1.0}).id)
        item = ModuleHigh(self.ch.type(attributes={Attribute.volume: 3501}).id, state=State.offline)
        fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.capital_item)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_item_other_class(self):
        fit = Fit()
        fit.ship = Ship(self.ch.type().id)
        item = Rig(self.ch.type(attributes={Attribute.volume: 3501}).id)
        fit.rigs.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.capital_item)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
