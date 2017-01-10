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


from unittest.mock import Mock, call

from eos.const.eos import State
from eos.fit.holder.item import Ship
from tests.stat_tracker.stat_testcase import StatTestCase


class TestEhp(StatTestCase):

    def test_relay(self):
        # Check that stat tracker relays ehp stats properly
        ship_item = self.ch.type_(type_id=1)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        ship_holder.get_ehp.return_value = Mock(hull=20, armor=30, shield=40, total=60)
        self.set_ship(ship_holder)
        damage_profile = Mock()
        ehp_calls_before = len(ship_holder.get_ehp.mock_calls)
        ehp_stats = self.st.get_ehp(damage_profile)
        ehp_calls_after = len(ship_holder.get_ehp.mock_calls)
        self.assertEqual(ehp_calls_after - ehp_calls_before, 1)
        self.assertEqual(ship_holder.get_ehp.mock_calls[-1], call.get_ehp(damage_profile))
        self.assertEqual(ehp_stats.hull, 20)
        self.assertEqual(ehp_stats.armor, 30)
        self.assertEqual(ehp_stats.shield, 40)
        self.assertEqual(ehp_stats.total, 60)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_no_ship(self):
        # Check that something sane is returned in case of no ship
        damage_profile = Mock()
        ehp_stats = self.st.get_ehp(damage_profile)
        self.assertIsNone(ehp_stats.hull)
        self.assertIsNone(ehp_stats.armor)
        self.assertIsNone(ehp_stats.shield)
        self.assertIsNone(ehp_stats.total)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()
