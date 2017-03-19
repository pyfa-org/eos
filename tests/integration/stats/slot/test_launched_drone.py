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
from eos.fit.item import Character, Drone, Implant
from tests.integration.stats.stat_testcase import StatTestCase


class TestLaunchedDrone(StatTestCase):

    def test_output(self):
        # Check that modified attribute of character is used
        char_eve_type = self.ch.type(type_id=1, attributes={Attribute.max_active_drones: 2})
        char_item = self.make_item_mock(Character, char_eve_type)
        char_item.attributes = {Attribute.max_active_drones: 6}
        self.set_character(char_item)
        self.assertEqual(self.ss.launched_drones.total, 6)
        self.set_character(None)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_output_no_ship(self):
        # None for max launched amount when no ship
        self.assertIsNone(self.ss.launched_drones.total)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_output_no_attr(self):
        # None for max launched amount when no attribute on ship
        char_eve_type = self.ch.type(type_id=1)
        char_item = self.make_item_mock(Character, char_eve_type)
        char_item.attributes = {}
        self.set_character(char_item)
        self.assertIsNone(self.ss.launched_drones.total)
        self.set_character(None)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_use_empty(self):
        self.assertEqual(self.ss.launched_drones.used, 0)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_use_single(self):
        eve_type = self.ch.type(type_id=1, attributes={})
        item = self.make_item_mock(Drone, eve_type, state=State.online)
        self.add_item(item)
        self.assertEqual(self.ss.launched_drones.used, 1)
        self.remove_item(item)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_use_multiple(self):
        eve_type = self.ch.type(type_id=1, attributes={})
        item1 = self.make_item_mock(Drone, eve_type, state=State.online)
        item2 = self.make_item_mock(Drone, eve_type, state=State.online)
        self.add_item(item1)
        self.add_item(item2)
        self.assertEqual(self.ss.launched_drones.used, 2)
        self.remove_item(item1)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_use_other_class(self):
        eve_type = self.ch.type(type_id=1, attributes={})
        item = self.make_item_mock(Implant, eve_type, state=State.online)
        self.add_item(item)
        self.assertEqual(self.ss.launched_drones.used, 0)
        self.remove_item(item)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_use_state(self):
        eve_type = self.ch.type(type_id=1, attributes={})
        item = self.make_item_mock(Drone, eve_type, state=State.offline)
        self.add_item(item)
        self.assertEqual(self.ss.launched_drones.used, 0)
        self.remove_item(item)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_cache(self):
        char_eve_type = self.ch.type(type_id=1)
        char_item = self.make_item_mock(Character, char_eve_type)
        char_item.attributes = {Attribute.max_active_drones: 6}
        self.set_character(char_item)
        eve_type = self.ch.type(type_id=2, attributes={})
        item1 = self.make_item_mock(Drone, eve_type, state=State.online)
        item2 = self.make_item_mock(Drone, eve_type, state=State.online)
        self.add_item(item1)
        self.add_item(item2)
        self.assertEqual(self.ss.launched_drones.used, 2)
        self.assertEqual(self.ss.launched_drones.total, 6)
        char_item.attributes[Attribute.max_active_drones] = 4
        self.remove_item(item1)
        self.assertEqual(self.ss.launched_drones.used, 2)
        self.assertEqual(self.ss.launched_drones.total, 6)
        self.set_character(None)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_volatility(self):
        char_eve_type = self.ch.type(type_id=1)
        char_item = self.make_item_mock(Character, char_eve_type)
        char_item.attributes = {Attribute.max_active_drones: 6}
        self.set_character(char_item)
        eve_type = self.ch.type(type_id=2, attributes={})
        item1 = self.make_item_mock(Drone, eve_type, state=State.online)
        item2 = self.make_item_mock(Drone, eve_type, state=State.online)
        self.add_item(item1)
        self.add_item(item2)
        self.assertEqual(self.ss.launched_drones.used, 2)
        self.assertEqual(self.ss.launched_drones.total, 6)
        char_item.attributes[Attribute.max_active_drones] = 4
        self.remove_item(item1)
        self.ss._clear_volatile_attrs()
        self.assertEqual(self.ss.launched_drones.used, 1)
        self.assertEqual(self.ss.launched_drones.total, 4)
        self.set_character(None)
        self.remove_item(item2)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
