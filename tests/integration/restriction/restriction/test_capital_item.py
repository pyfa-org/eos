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


from eos import ModuleHigh
from eos import Restriction
from eos import Rig
from eos import Ship
from eos import State
from eos.const.eve import AttrId
from tests.integration.restriction.testcase import RestrictionTestCase


class TestCapitalItem(RestrictionTestCase):
    """Check functionality of capital-sized modules restriction."""

    def test_fail_ship_absent(self):
        # Check that error is raised on attempt to add capital item to fit w/o
        # ship
        item = ModuleHigh(
            self.mktype(attrs={AttrId.volume: 3501}).id,
            state=State.offline)
        self.fit.modules.high.append(item)
        # Action
        error = self.get_error(item, Restriction.capital_item)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_volume, 3501)
        self.assertEqual(error.max_subcap_volume, 3500)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_ship_not_loaded(self):
        # Ship which is not loaded is considered as ship absence, i.e. not
        # capital ship
        self.fit.ship = Ship(self.allocate_type_id())
        item = ModuleHigh(
            self.mktype(attrs={AttrId.volume: 3501}).id,
            state=State.offline)
        self.fit.modules.high.append(item)
        # Action
        error = self.get_error(item, Restriction.capital_item)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_volume, 3501)
        self.assertEqual(error.max_subcap_volume, 3500)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_ship_attr_absent(self):
        self.fit.ship = Ship(self.mktype().id)
        item = ModuleHigh(
            self.mktype(attrs={AttrId.volume: 3501}).id,
            state=State.offline)
        self.fit.modules.high.append(item)
        # Action
        error = self.get_error(item, Restriction.capital_item)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_volume, 3501)
        self.assertEqual(error.max_subcap_volume, 3500)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_ship_attr_zero(self):
        # Make sure that mere presence of isCapital attr on a ship (with zero
        # value) doesn't make it capital
        self.fit.ship = Ship(self.mktype(
            attrs={AttrId.is_capital_size: 0.0}).id)
        item = ModuleHigh(
            self.mktype(attrs={AttrId.volume: 3501}).id,
            state=State.offline)
        self.fit.modules.high.append(item)
        # Action
        error = self.get_error(item, Restriction.capital_item)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_volume, 3501)
        self.assertEqual(error.max_subcap_volume, 3500)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_ship_attr_capital(self):
        # Check that capital items can be added to capital ship
        self.fit.ship = Ship(self.mktype(
            attrs={AttrId.is_capital_size: 1.0}).id)
        item = ModuleHigh(
            self.mktype(attrs={AttrId.volume: 3501}).id,
            state=State.offline)
        self.fit.modules.high.append(item)
        # Action
        error = self.get_error(item, Restriction.capital_item)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_item_subcap(self):
        # Make sure no error raised when non-capital item is added to fit
        item = ModuleHigh(
            self.mktype(attrs={AttrId.volume: 3500}).id,
            state=State.offline)
        self.fit.modules.high.append(item)
        # Action
        error = self.get_error(item, Restriction.capital_item)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_item_attr_absent(self):
        # Check that items with no volume attribute on item type are not
        # restricted
        item = ModuleHigh(self.mktype().id, state=State.offline)
        self.fit.modules.high.append(item)
        self.fit.ship = Ship(self.mktype().id)
        # Action
        error = self.get_error(item, Restriction.capital_item)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_item_not_loaded(self):
        # Not loaded items do not generate errors
        self.fit.ship = Ship(self.mktype().id)
        item = ModuleHigh(self.allocate_type_id(), state=State.offline)
        self.fit.modules.high.append(item)
        # Action
        error = self.get_error(item, Restriction.capital_item)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_item_other_class(self):
        self.fit.ship = Ship(self.mktype().id)
        item = Rig(self.mktype(attrs={AttrId.volume: 3501}).id)
        self.fit.rigs.add(item)
        # Action
        error = self.get_error(item, Restriction.capital_item)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
