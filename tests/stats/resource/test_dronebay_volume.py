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


from eos.const.eos import State
from eos.const.eve import Attribute
from eos.fit.item import Drone, Ship
from tests.stats.stat_testcase import StatTestCase


class TestDroneBayVolume(StatTestCase):
    """Check functionality of drone bay volume stats"""

    def test_output(self):
        # Check that modified attribute of ship is used
        ship_eve_type = self.ch.type(type_id=1, attributes={Attribute.drone_capacity: 10})
        ship_item = self.make_item_mock(Ship, ship_eve_type)
        ship_item.attributes = {Attribute.drone_capacity: 50}
        self.set_ship(ship_item)
        self.assertEqual(self.ss.dronebay.output, 50)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_output_no_ship(self):
        # None for output when no ship
        self.assertIsNone(self.ss.dronebay.output)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_output_no_attr(self):
        # None for output when no attribute on ship
        ship_eve_type = self.ch.type(type_id=1)
        ship_item = self.make_item_mock(Ship, ship_eve_type)
        ship_item.attributes = {}
        self.set_ship(ship_item)
        self.assertIsNone(self.ss.dronebay.output)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_single_no_rounding(self):
        eve_type = self.ch.type(type_id=1, attributes={Attribute.volume: 0})
        item = self.make_item_mock(Drone, eve_type, state=State.offline)
        item.attributes = {Attribute.volume: 55.5555555555}
        self.fit.drones.add(item)
        self.add_item(item)
        self.assertEqual(self.ss.dronebay.used, 55.5555555555)
        self.remove_item(item)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_multiple(self):
        eve_type = self.ch.type(type_id=1, attributes={Attribute.volume: 0})
        item1 = self.make_item_mock(Drone, eve_type, state=State.offline)
        item1.attributes = {Attribute.volume: 50}
        self.fit.drones.add(item1)
        self.add_item(item1)
        item2 = self.make_item_mock(Drone, eve_type, state=State.offline)
        item2.attributes = {Attribute.volume: 30}
        self.fit.drones.add(item2)
        self.add_item(item2)
        self.assertEqual(self.ss.dronebay.used, 80)
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_negative(self):
        eve_type = self.ch.type(type_id=1, attributes={Attribute.volume: 0})
        item1 = self.make_item_mock(Drone, eve_type, state=State.offline)
        item1.attributes = {Attribute.volume: 50}
        self.fit.drones.add(item1)
        self.add_item(item1)
        item2 = self.make_item_mock(Drone, eve_type, state=State.offline)
        item2.attributes = {Attribute.volume: -30}
        self.fit.drones.add(item2)
        self.add_item(item2)
        self.assertEqual(self.ss.dronebay.used, 20)
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_none(self):
        self.assertEqual(self.ss.dronebay.used, 0)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_other_class(self):
        # Make sure items placed to other containers are unaffected
        eve_type = self.ch.type(type_id=1, attributes={Attribute.volume: 0})
        item = self.make_item_mock(Drone, eve_type, state=State.offline)
        item.attributes = {Attribute.volume: 30}
        self.fit.rigs.add(item)
        self.add_item(item)
        self.assertEqual(self.ss.dronebay.used, 0)
        self.remove_item(item)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_cache(self):
        ship_eve_type = self.ch.type(type_id=1, attributes={Attribute.drone_capacity: 10})
        ship_item = self.make_item_mock(Ship, ship_eve_type)
        ship_item.attributes = {Attribute.drone_capacity: 50}
        self.set_ship(ship_item)
        eve_type = self.ch.type(type_id=2, attributes={Attribute.volume: 0})
        item1 = self.make_item_mock(Drone, eve_type, state=State.offline)
        item1.attributes = {Attribute.volume: 50}
        self.fit.drones.add(item1)
        self.add_item(item1)
        item2 = self.make_item_mock(Drone, eve_type, state=State.offline)
        item2.attributes = {Attribute.volume: 30}
        self.fit.drones.add(item2)
        self.add_item(item2)
        self.assertEqual(self.ss.dronebay.used, 80)
        self.assertEqual(self.ss.dronebay.output, 50)
        item1.attributes[Attribute.volume] = 10
        ship_item.attributes[Attribute.drone_capacity] = 60
        self.assertEqual(self.ss.dronebay.used, 80)
        self.assertEqual(self.ss.dronebay.output, 50)
        self.set_ship(None)
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_volatility(self):
        ship_eve_type = self.ch.type(type_id=1, attributes={Attribute.drone_capacity: 10})
        ship_item = self.make_item_mock(Ship, ship_eve_type)
        ship_item.attributes = {Attribute.drone_capacity: 50}
        self.set_ship(ship_item)
        eve_type = self.ch.type(type_id=2, attributes={Attribute.volume: 0})
        item1 = self.make_item_mock(Drone, eve_type, state=State.offline)
        item1.attributes = {Attribute.volume: 50}
        self.fit.drones.add(item1)
        self.add_item(item1)
        item2 = self.make_item_mock(Drone, eve_type, state=State.offline)
        item2.attributes = {Attribute.volume: 30}
        self.fit.drones.add(item2)
        self.add_item(item2)
        self.assertEqual(self.ss.dronebay.used, 80)
        self.assertEqual(self.ss.dronebay.output, 50)
        item1.attributes[Attribute.volume] = 10
        ship_item.attributes[Attribute.drone_capacity] = 60
        self.ss._clear_volatile_attrs()
        self.assertEqual(self.ss.dronebay.used, 40)
        self.assertEqual(self.ss.dronebay.output, 60)
        self.set_ship(None)
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()
