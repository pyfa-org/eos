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


from unittest.mock import Mock

from eos.fit.item import Ship
from tests.stats.stat_testcase import StatTestCase


class TestWorstCaseEhp(StatTestCase):

    def test_relay(self):
        # Check that stats service relays wcehp stats properly
        ship_eve_type = self.ch.type(type_id=1)
        ship_item = self.make_item_mock(Ship, ship_eve_type)
        ship_item.worst_case_ehp.hull = 50
        ship_item.worst_case_ehp.armor = 60
        ship_item.worst_case_ehp.shield = 70
        ship_item.worst_case_ehp.total = 80
        self.set_ship(ship_item)
        self.assertEqual(self.ss.worst_case_ehp.hull, 50)
        self.assertEqual(self.ss.worst_case_ehp.armor, 60)
        self.assertEqual(self.ss.worst_case_ehp.shield, 70)
        self.assertEqual(self.ss.worst_case_ehp.total, 80)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_no_ship(self):
        # Check that something sane is returned in case of no ship
        self.assertIsNone(self.ss.worst_case_ehp.hull)
        self.assertIsNone(self.ss.worst_case_ehp.armor)
        self.assertIsNone(self.ss.worst_case_ehp.shield)
        self.assertIsNone(self.ss.worst_case_ehp.total)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_cache(self):
        ship_eve_type = self.ch.type(type_id=1)
        ship_item = self.make_item_mock(Ship, ship_eve_type)
        self.set_ship(ship_item)
        ship_item.worst_case_ehp = Mock(hull=50, armor=60, shield=70, total=80)
        self.assertEqual(self.ss.worst_case_ehp.hull, 50)
        self.assertEqual(self.ss.worst_case_ehp.armor, 60)
        self.assertEqual(self.ss.worst_case_ehp.shield, 70)
        self.assertEqual(self.ss.worst_case_ehp.total, 80)
        ship_item.worst_case_ehp = Mock(hull=150, armor=160, shield=170, total=180)
        self.assertEqual(self.ss.worst_case_ehp.hull, 50)
        self.assertEqual(self.ss.worst_case_ehp.armor, 60)
        self.assertEqual(self.ss.worst_case_ehp.shield, 70)
        self.assertEqual(self.ss.worst_case_ehp.total, 80)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_volatility(self):
        ship_eve_type = self.ch.type(type_id=1)
        ship_item = self.make_item_mock(Ship, ship_eve_type)
        self.set_ship(ship_item)
        ship_item.worst_case_ehp = Mock(hull=50, armor=60, shield=70, total=80)
        self.assertEqual(self.ss.worst_case_ehp.hull, 50)
        self.assertEqual(self.ss.worst_case_ehp.armor, 60)
        self.assertEqual(self.ss.worst_case_ehp.shield, 70)
        self.assertEqual(self.ss.worst_case_ehp.total, 80)
        ship_item.worst_case_ehp = Mock(hull=150, armor=160, shield=170, total=180)
        self.ss._clear_volatile_attrs()
        self.assertEqual(self.ss.worst_case_ehp.hull, 150)
        self.assertEqual(self.ss.worst_case_ehp.armor, 160)
        self.assertEqual(self.ss.worst_case_ehp.shield, 170)
        self.assertEqual(self.ss.worst_case_ehp.total, 180)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()
