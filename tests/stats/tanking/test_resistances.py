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

from eos.const.eos import State
from eos.fit.holder.item import Ship
from tests.stat_tracker.stat_testcase import StatTestCase


class TestResistances(StatTestCase):

    def test_relay(self):
        # Check that stat tracker relays resistance stats properly
        ship_item = self.ch.type_(type_id=1)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        ship_holder.resistances.hull.em = 5
        ship_holder.resistances.hull.thermal = 6
        ship_holder.resistances.hull.kinetic = 7
        ship_holder.resistances.hull.explosive = 8
        ship_holder.resistances.armor.em = 15
        ship_holder.resistances.armor.thermal = 16
        ship_holder.resistances.armor.kinetic = 17
        ship_holder.resistances.armor.explosive = 18
        ship_holder.resistances.shield.em = 25
        ship_holder.resistances.shield.thermal = 26
        ship_holder.resistances.shield.kinetic = 27
        ship_holder.resistances.shield.explosive = 28
        self.set_ship(ship_holder)
        self.assertEqual(self.st.resistances.hull.em, 5)
        self.assertEqual(self.st.resistances.hull.thermal, 6)
        self.assertEqual(self.st.resistances.hull.kinetic, 7)
        self.assertEqual(self.st.resistances.hull.explosive, 8)
        self.assertEqual(self.st.resistances.armor.em, 15)
        self.assertEqual(self.st.resistances.armor.thermal, 16)
        self.assertEqual(self.st.resistances.armor.kinetic, 17)
        self.assertEqual(self.st.resistances.armor.explosive, 18)
        self.assertEqual(self.st.resistances.shield.em, 25)
        self.assertEqual(self.st.resistances.shield.thermal, 26)
        self.assertEqual(self.st.resistances.shield.kinetic, 27)
        self.assertEqual(self.st.resistances.shield.explosive, 28)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_no_ship(self):
        # Check that something sane is returned in case of no ship
        self.assertIsNone(self.st.resistances.hull.em)
        self.assertIsNone(self.st.resistances.hull.thermal)
        self.assertIsNone(self.st.resistances.hull.kinetic)
        self.assertIsNone(self.st.resistances.hull.explosive)
        self.assertIsNone(self.st.resistances.armor.em)
        self.assertIsNone(self.st.resistances.armor.thermal)
        self.assertIsNone(self.st.resistances.armor.kinetic)
        self.assertIsNone(self.st.resistances.armor.explosive)
        self.assertIsNone(self.st.resistances.shield.em)
        self.assertIsNone(self.st.resistances.shield.thermal)
        self.assertIsNone(self.st.resistances.shield.kinetic)
        self.assertIsNone(self.st.resistances.shield.explosive)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_cache(self):
        ship_item = self.ch.type_(type_id=1)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        hull = Mock(em=5, thermal=6, kinetic=7, explosive=8)
        armor = Mock(em=15, thermal=16, kinetic=17, explosive=18)
        shield = Mock(em=25, thermal=26, kinetic=27, explosive=28)
        ship_holder.resistances = Mock(hull=hull, armor=armor, shield=shield)
        self.assertEqual(self.st.resistances.hull.em, 5)
        self.assertEqual(self.st.resistances.hull.thermal, 6)
        self.assertEqual(self.st.resistances.hull.kinetic, 7)
        self.assertEqual(self.st.resistances.hull.explosive, 8)
        self.assertEqual(self.st.resistances.armor.em, 15)
        self.assertEqual(self.st.resistances.armor.thermal, 16)
        self.assertEqual(self.st.resistances.armor.kinetic, 17)
        self.assertEqual(self.st.resistances.armor.explosive, 18)
        self.assertEqual(self.st.resistances.shield.em, 25)
        self.assertEqual(self.st.resistances.shield.thermal, 26)
        self.assertEqual(self.st.resistances.shield.kinetic, 27)
        self.assertEqual(self.st.resistances.shield.explosive, 28)
        hull = Mock(em=15, thermal=16, kinetic=17, explosive=18)
        armor = Mock(em=25, thermal=26, kinetic=27, explosive=28)
        shield = Mock(em=35, thermal=36, kinetic=37, explosive=38)
        ship_holder.resistances = Mock(hull=hull, armor=armor, shield=shield)
        self.assertEqual(self.st.resistances.hull.em, 5)
        self.assertEqual(self.st.resistances.hull.thermal, 6)
        self.assertEqual(self.st.resistances.hull.kinetic, 7)
        self.assertEqual(self.st.resistances.hull.explosive, 8)
        self.assertEqual(self.st.resistances.armor.em, 15)
        self.assertEqual(self.st.resistances.armor.thermal, 16)
        self.assertEqual(self.st.resistances.armor.kinetic, 17)
        self.assertEqual(self.st.resistances.armor.explosive, 18)
        self.assertEqual(self.st.resistances.shield.em, 25)
        self.assertEqual(self.st.resistances.shield.thermal, 26)
        self.assertEqual(self.st.resistances.shield.kinetic, 27)
        self.assertEqual(self.st.resistances.shield.explosive, 28)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_volatility(self):
        ship_item = self.ch.type_(type_id=1)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        hull = Mock(em=5, thermal=6, kinetic=7, explosive=8)
        armor = Mock(em=15, thermal=16, kinetic=17, explosive=18)
        shield = Mock(em=25, thermal=26, kinetic=27, explosive=28)
        ship_holder.resistances = Mock(hull=hull, armor=armor, shield=shield)
        self.assertEqual(self.st.resistances.hull.em, 5)
        self.assertEqual(self.st.resistances.hull.thermal, 6)
        self.assertEqual(self.st.resistances.hull.kinetic, 7)
        self.assertEqual(self.st.resistances.hull.explosive, 8)
        self.assertEqual(self.st.resistances.armor.em, 15)
        self.assertEqual(self.st.resistances.armor.thermal, 16)
        self.assertEqual(self.st.resistances.armor.kinetic, 17)
        self.assertEqual(self.st.resistances.armor.explosive, 18)
        self.assertEqual(self.st.resistances.shield.em, 25)
        self.assertEqual(self.st.resistances.shield.thermal, 26)
        self.assertEqual(self.st.resistances.shield.kinetic, 27)
        self.assertEqual(self.st.resistances.shield.explosive, 28)
        hull = Mock(em=15, thermal=16, kinetic=17, explosive=18)
        armor = Mock(em=25, thermal=26, kinetic=27, explosive=28)
        shield = Mock(em=35, thermal=36, kinetic=37, explosive=38)
        ship_holder.resistances = Mock(hull=hull, armor=armor, shield=shield)
        self.st._clear_volatile_attrs()
        self.assertEqual(self.st.resistances.hull.em, 15)
        self.assertEqual(self.st.resistances.hull.thermal, 16)
        self.assertEqual(self.st.resistances.hull.kinetic, 17)
        self.assertEqual(self.st.resistances.hull.explosive, 18)
        self.assertEqual(self.st.resistances.armor.em, 25)
        self.assertEqual(self.st.resistances.armor.thermal, 26)
        self.assertEqual(self.st.resistances.armor.kinetic, 27)
        self.assertEqual(self.st.resistances.armor.explosive, 28)
        self.assertEqual(self.st.resistances.shield.em, 35)
        self.assertEqual(self.st.resistances.shield.thermal, 36)
        self.assertEqual(self.st.resistances.shield.kinetic, 37)
        self.assertEqual(self.st.resistances.shield.explosive, 38)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()
