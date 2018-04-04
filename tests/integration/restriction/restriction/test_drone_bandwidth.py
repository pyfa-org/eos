# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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
from eos import Restriction
from eos import Ship
from eos import State
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from tests.integration.restriction.testcase import RestrictionTestCase


class TestDroneBandwidth(RestrictionTestCase):
    """Check functionality of drone bandwidth restriction."""

    def setUp(self):
        RestrictionTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.drone_bandwidth)
        self.mkattr(attr_id=AttrId.drone_bandwidth_used)

    def test_fail_single(self):
        # When ship provides drone bandwidth output, but single consumer demands
        # for more, error should be raised
        self.fit.ship = Ship(self.mktype(
            attrs={AttrId.drone_bandwidth: 40}).id)
        item = Drone(
            self.mktype(attrs={AttrId.drone_bandwidth_used: 50}).id,
            state=State.online)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.output, 40)
        self.assertEqual(error.total_use, 50)
        self.assertEqual(error.item_use, 50)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_multiple(self):
        # When multiple consumers require less than drone bandwidth output
        # alone, but in sum want more than total output, it should be erroneous
        # situation
        self.fit.ship = Ship(self.mktype(
            attrs={AttrId.drone_bandwidth: 40}).id)
        item1 = Drone(
            self.mktype(attrs={AttrId.drone_bandwidth_used: 25}).id,
            state=State.online)
        self.fit.drones.add(item1)
        item2 = Drone(
            self.mktype(attrs={AttrId.drone_bandwidth_used: 20}).id,
            state=State.online)
        self.fit.drones.add(item2)
        # Action
        error1 = self.get_error(item1, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNotNone(error1)
        self.assertEqual(error1.output, 40)
        self.assertEqual(error1.total_use, 45)
        self.assertEqual(error1.item_use, 25)
        # Action
        error2 = self.get_error(item2, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNotNone(error2)
        self.assertEqual(error2.output, 40)
        self.assertEqual(error2.total_use, 45)
        self.assertEqual(error2.item_use, 20)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_modified(self):
        # Make sure modified drone bandwidth values are taken
        self.fit.ship = Ship(self.mktype(
            attrs={AttrId.drone_bandwidth: 50}).id)
        src_attr = self.mkattr()
        modifier = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=AttrId.drone_bandwidth_used,
            operator=ModOperator.post_mul,
            src_attr_id=src_attr.id)
        effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier])
        item = Drone(
            self.mktype(
                attrs={AttrId.drone_bandwidth_used: 50, src_attr.id: 2},
                effects=[effect]).id,
            state=State.online)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.output, 50)
        self.assertEqual(error.total_use, 100)
        self.assertEqual(error.item_use, 100)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_ship_absent(self):
        # When stats module does not specify output, make sure it's assumed to
        # be 0
        item = Drone(
            self.mktype(attrs={AttrId.drone_bandwidth_used: 5}).id,
            state=State.online)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.output, 0)
        self.assertEqual(error.total_use, 5)
        self.assertEqual(error.item_use, 5)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_ship_attr_absent(self):
        self.fit.ship = Ship(self.mktype().id)
        item = Drone(
            self.mktype(attrs={AttrId.drone_bandwidth_used: 50}).id,
            state=State.online)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.output, 0)
        self.assertEqual(error.total_use, 50)
        self.assertEqual(error.item_use, 50)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_ship_not_loaded(self):
        self.fit.ship = Ship(self.allocate_type_id())
        item = Drone(
            self.mktype(attrs={AttrId.drone_bandwidth_used: 5}).id,
            state=State.online)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.output, 0)
        self.assertEqual(error.total_use, 5)
        self.assertEqual(error.item_use, 5)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_mix_usage_zero(self):
        # If some item has zero usage and drone bandwidth error is still raised,
        # check it's not raised for item with zero usage
        self.fit.ship = Ship(self.mktype(
            attrs={AttrId.drone_bandwidth: 50}).id)
        item1 = Drone(
            self.mktype(attrs={AttrId.drone_bandwidth_used: 100}).id,
            state=State.online)
        self.fit.drones.add(item1)
        item2 = Drone(
            self.mktype(attrs={AttrId.drone_bandwidth_used: 0}).id,
            state=State.online)
        self.fit.drones.add(item2)
        # Action
        error1 = self.get_error(item1, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNotNone(error1)
        self.assertEqual(error1.output, 50)
        self.assertEqual(error1.total_use, 100)
        self.assertEqual(error1.item_use, 100)
        # Action
        error2 = self.get_error(item2, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNone(error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass(self):
        # When total consumption is less than output, no errors should be raised
        self.fit.ship = Ship(self.mktype(
            attrs={AttrId.drone_bandwidth: 50}).id)
        item1 = Drone(
            self.mktype(attrs={AttrId.drone_bandwidth_used: 25}).id,
            state=State.online)
        self.fit.drones.add(item1)
        item2 = Drone(
            self.mktype(attrs={AttrId.drone_bandwidth_used: 20}).id,
            state=State.online)
        self.fit.drones.add(item2)
        # Action
        error1 = self.get_error(item1, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNone(error1)
        # Action
        error2 = self.get_error(item2, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNone(error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_item_state(self):
        # When item isn't online, it shouldn't consume anything
        self.fit.ship = Ship(self.mktype(
            attrs={AttrId.drone_bandwidth: 40}).id)
        item = Drone(
            self.mktype(attrs={AttrId.drone_bandwidth_used: 50}).id,
            state=State.offline)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_item_attr_absent(self):
        self.fit.ship = Ship(self.mktype(
            attrs={AttrId.drone_bandwidth: 40}).id)
        item = Drone(self.mktype().id, state=State.online)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_item_not_loaded(self):
        self.fit.ship = Ship(self.mktype(
            attrs={AttrId.drone_bandwidth: 0}).id)
        item = Drone(self.allocate_type_id(), state=State.online)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.drone_bandwidth)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
