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


class TestWorstCaseEhp(StatTestCase):

    def test_relay(self):
        # Check that stat tracker relays wcehp stats properly
        ship_item = self.ch.type_(type_id=1)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        ship_holder.worst_case_ehp.hull = 50
        ship_holder.worst_case_ehp.armor = 60
        ship_holder.worst_case_ehp.shield = 70
        ship_holder.worst_case_ehp.total = 80
        self.set_ship(ship_holder)
        self.assertEqual(self.st.worst_case_ehp.hull, 50)
        self.assertEqual(self.st.worst_case_ehp.armor, 60)
        self.assertEqual(self.st.worst_case_ehp.shield, 70)
        self.assertEqual(self.st.worst_case_ehp.total, 80)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_no_ship(self):
        # Check that something sane is returned in case of no ship
        self.assertIsNone(self.st.worst_case_ehp.hull)
        self.assertIsNone(self.st.worst_case_ehp.armor)
        self.assertIsNone(self.st.worst_case_ehp.shield)
        self.assertIsNone(self.st.worst_case_ehp.total)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_cache(self):
        ship_item = self.ch.type_(type_id=1)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        ship_holder.worst_case_ehp = Mock(hull=50, armor=60, shield=70, total=80)
        self.assertEqual(self.st.worst_case_ehp.hull, 50)
        self.assertEqual(self.st.worst_case_ehp.armor, 60)
        self.assertEqual(self.st.worst_case_ehp.shield, 70)
        self.assertEqual(self.st.worst_case_ehp.total, 80)
        ship_holder.worst_case_ehp = Mock(hull=150, armor=160, shield=170, total=180)
        self.assertEqual(self.st.worst_case_ehp.hull, 50)
        self.assertEqual(self.st.worst_case_ehp.armor, 60)
        self.assertEqual(self.st.worst_case_ehp.shield, 70)
        self.assertEqual(self.st.worst_case_ehp.total, 80)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_volatility(self):
        ship_item = self.ch.type_(type_id=1)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        self.set_ship(ship_holder)
        ship_holder.worst_case_ehp = Mock(hull=50, armor=60, shield=70, total=80)
        self.assertEqual(self.st.worst_case_ehp.hull, 50)
        self.assertEqual(self.st.worst_case_ehp.armor, 60)
        self.assertEqual(self.st.worst_case_ehp.shield, 70)
        self.assertEqual(self.st.worst_case_ehp.total, 80)
        ship_holder.worst_case_ehp = Mock(hull=150, armor=160, shield=170, total=180)
        self.st._clear_volatile_attrs()
        self.assertEqual(self.st.worst_case_ehp.hull, 150)
        self.assertEqual(self.st.worst_case_ehp.armor, 160)
        self.assertEqual(self.st.worst_case_ehp.shield, 170)
        self.assertEqual(self.st.worst_case_ehp.total, 180)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()
