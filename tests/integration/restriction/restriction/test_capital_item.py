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
from eos.const.eve import AttrId
from tests.integration.restriction.restriction_testcase import (
    RestrictionTestCase)


class TestCapitalItem(RestrictionTestCase):
    """Check functionality of capital-sized modules restriction."""

    def test_fail_no_ship(self):
        # Check that error is raised on attempt to add capital item to fit w/o
        # ship
        item = ModuleHigh(
            self.ch.type(attrs={AttrId.volume: 3501}).id,
            state=State.offline)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.capital_item)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_volume, 3501)
        self.assertEqual(restriction_error.max_subcap_volume, 3500)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_subcap(self):
        self.fit.ship = Ship(self.ch.type().id)
        item = ModuleHigh(
            self.ch.type(attrs={AttrId.volume: 3501}).id,
            state=State.offline)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.capital_item)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_volume, 3501)
        self.assertEqual(restriction_error.max_subcap_volume, 3500)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_subcap_capattr_zero(self):
        # Make sure that mere presence of isCapital attr on a ship (with zero
        # value) doesn't make it capital
        self.fit.ship = Ship(self.ch.type(
            attrs={AttrId.is_capital_size: 0.0}).id)
        item = ModuleHigh(
            self.ch.type(attrs={AttrId.volume: 3501}).id,
            state=State.offline)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.capital_item)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_volume, 3501)
        self.assertEqual(restriction_error.max_subcap_volume, 3500)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_subcap_volume_subcap(self):
        # Make sure no error raised when non-capital item is added to fit
        item = ModuleHigh(
            self.ch.type(attrs={AttrId.volume: 3500}).id,
            state=State.offline)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.capital_item)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_subcap_volume_not_specified(self):
        # Check that items with no volume attribute on item type are not
        # restricted
        item = ModuleHigh(self.ch.type().id, state=State.offline)
        self.fit.modules.high.append(item)
        self.fit.ship = Ship(self.ch.type().id)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.capital_item)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_capital(self):
        # Check that capital items can be added to capital ship
        self.fit.ship = Ship(self.ch.type(
            attrs={AttrId.is_capital_size: 1.0}).id)
        item = ModuleHigh(
            self.ch.type(attrs={AttrId.volume: 3501}).id,
            state=State.offline)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.capital_item)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_item_other_class(self):
        self.fit.ship = Ship(self.ch.type().id)
        item = Rig(self.ch.type(attrs={AttrId.volume: 3501}).id)
        self.fit.rigs.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.capital_item)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_no_source(self):
        self.fit.ship = Ship(self.ch.type().id)
        item = ModuleHigh(
            self.ch.type(attrs={AttrId.volume: 3501}).id,
            state=State.offline)
        self.fit.modules.high.append(item)
        self.fit.source = None
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.capital_item)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
