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


from eos import Drone
from eos import ModuleHigh
from eos import Restriction
from eos import Ship
from eos.const.eve import AttrId
from tests.integration.restriction.testcase import RestrictionTestCase


class TestDroneBayVolume(RestrictionTestCase):
    """Check functionality of drone bay volume restriction."""

    def setUp(self):
        RestrictionTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.volume)
        self.mkattr(attr_id=AttrId.drone_capacity)

    def test_fail_excess_single(self):
        # When ship provides dronebay volume output, but single consumer demands
        # for more, error should be raised
        self.fit.ship = Ship(self.mktype(attrs={AttrId.drone_capacity: 40}).id)
        item = Drone(self.mktype(attrs={AttrId.volume: 50}).id)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.dronebay_volume)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.output, 40)
        self.assertEqual(error.total_use, 50)
        self.assertEqual(error.item_use, 50)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_excess_single_undefined_output(self):
        # When stats module does not specify output, make sure it's assumed to
        # be 0
        item = Drone(self.mktype(attrs={AttrId.volume: 5}).id)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.dronebay_volume)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.output, 0)
        self.assertEqual(error.total_use, 5)
        self.assertEqual(error.item_use, 5)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_excess_multiple(self):
        # When multiple consumers require less than dronebay volume output
        # alone, but in sum want more than total output, it should be erroneous
        # situation
        self.fit.ship = Ship(self.mktype(attrs={AttrId.drone_capacity: 40}).id)
        item1 = Drone(self.mktype(attrs={AttrId.volume: 25}).id)
        self.fit.drones.add(item1)
        item2 = Drone(self.mktype(attrs={AttrId.volume: 20}).id)
        self.fit.drones.add(item2)
        # Action
        error1 = self.get_error(item1, Restriction.dronebay_volume)
        # Verification
        self.assertIsNotNone(error1)
        self.assertEqual(error1.output, 40)
        self.assertEqual(error1.total_use, 45)
        self.assertEqual(error1.item_use, 25)
        # Action
        error2 = self.get_error(item2, Restriction.dronebay_volume)
        # Verification
        self.assertIsNotNone(error2)
        self.assertEqual(error2.output, 40)
        self.assertEqual(error2.total_use, 45)
        self.assertEqual(error2.item_use, 20)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_mix_usage_zero(self):
        # If some item has zero usage and dronebay volume error is still raised,
        # check it's not raised for item with zero usage
        self.fit.ship = Ship(self.mktype(attrs={AttrId.drone_capacity: 50}).id)
        item1 = Drone(self.mktype(attrs={AttrId.volume: 100}).id)
        self.fit.drones.add(item1)
        item2 = Drone(self.mktype(attrs={AttrId.volume: 0}).id)
        self.fit.drones.add(item2)
        # Action
        error1 = self.get_error(item1, Restriction.dronebay_volume)
        # Verification
        self.assertIsNotNone(error1)
        self.assertEqual(error1.output, 50)
        self.assertEqual(error1.total_use, 100)
        self.assertEqual(error1.item_use, 100)
        # Action
        error2 = self.get_error(item2, Restriction.dronebay_volume)
        # Verification
        self.assertIsNone(error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass(self):
        # When total consumption is less than output, no errors should be raised
        self.fit.ship = Ship(self.mktype(attrs={AttrId.drone_capacity: 50}).id)
        item1 = Drone(self.mktype(attrs={AttrId.volume: 25}).id)
        self.fit.drones.add(item1)
        item2 = Drone(self.mktype(attrs={AttrId.volume: 20}).id)
        self.fit.drones.add(item2)
        # Action
        error1 = self.get_error(item1, Restriction.dronebay_volume)
        # Verification
        self.assertIsNone(error1)
        # Action
        error2 = self.get_error(item2, Restriction.dronebay_volume)
        # Verification
        self.assertIsNone(error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_other_class(self):
        # Make sure non-drones are not affected
        self.fit.ship = Ship(self.mktype(attrs={AttrId.drone_capacity: 40}).id)
        item = ModuleHigh(self.mktype(attrs={AttrId.volume: 50}).id)
        self.fit.modules.high.append(item)
        # Action
        error = self.get_error(item, Restriction.dronebay_volume)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_no_source(self):
        self.fit.ship = Ship(self.mktype(attrs={AttrId.drone_capacity: 40}).id)
        item = Drone(self.mktype(attrs={AttrId.volume: 50}).id)
        self.fit.drones.add(item)
        self.fit.source = None
        # Action
        error = self.get_error(item, Restriction.dronebay_volume)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
