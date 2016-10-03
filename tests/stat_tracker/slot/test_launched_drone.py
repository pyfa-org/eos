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

from eos.const.eos import Domain, State
from eos.const.eve import Attribute
from eos.fit.holder.item import Character, Drone, Implant
from tests.stat_tracker.stat_testcase import StatTestCase


class TestLaunchedDrone(StatTestCase):

    def test_output(self):
        # Check that modified attribute of character is used
        char_item = self.ch.type_(type_id=1, attributes={Attribute.max_active_drones: 2})
        char_holder = Mock(state=State.offline, item=char_item, _domain=None, spec_set=Character(1))
        char_holder.attributes = {Attribute.max_active_drones: 6}
        self.set_character(char_holder)
        self.assertEqual(self.st.launched_drones.total, 6)
        self.set_character(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_output_no_ship(self):
        # None for max launched amount when no ship
        self.assertIsNone(self.st.launched_drones.total)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_output_no_attr(self):
        # None for max launched amount when no attribute on ship
        char_item = self.ch.type_(type_id=1)
        char_holder = Mock(state=State.offline, item=char_item, _domain=None, spec_set=Character(1))
        char_holder.attributes = {}
        self.set_character(char_holder)
        self.assertIsNone(self.st.launched_drones.total)
        self.set_character(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_empty(self):
        self.assertEqual(self.st.launched_drones.used, 0)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_single(self):
        item = self.ch.type_(type_id=1, attributes={})
        holder = Mock(state=State.online, item=item, _domain=Domain.space, spec_set=Drone(1))
        self.track_holder(holder)
        self.assertEqual(self.st.launched_drones.used, 1)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_multiple(self):
        item = self.ch.type_(type_id=1, attributes={})
        holder1 = Mock(state=State.online, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder2 = Mock(state=State.online, item=item, _domain=Domain.space, spec_set=Drone(1))
        self.track_holder(holder1)
        self.track_holder(holder2)
        self.assertEqual(self.st.launched_drones.used, 2)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_other_class(self):
        item = self.ch.type_(type_id=1, attributes={})
        holder = Mock(state=State.online, item=item, _domain=Domain.space, spec_set=Implant(1))
        self.track_holder(holder)
        self.assertEqual(self.st.launched_drones.used, 0)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_state(self):
        item = self.ch.type_(type_id=1, attributes={})
        holder = Mock(state=State.offline, item=item, _domain=Domain.space, spec_set=Drone(1))
        self.track_holder(holder)
        self.assertEqual(self.st.launched_drones.used, 0)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_cache(self):
        char_item = self.ch.type_(type_id=1)
        char_holder = Mock(state=State.offline, item=char_item, _domain=None, spec_set=Character(1))
        char_holder.attributes = {Attribute.max_active_drones: 6}
        self.set_character(char_holder)
        item = self.ch.type_(type_id=2, attributes={})
        holder1 = Mock(state=State.online, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder2 = Mock(state=State.online, item=item, _domain=Domain.space, spec_set=Drone(1))
        self.track_holder(holder1)
        self.track_holder(holder2)
        self.assertEqual(self.st.launched_drones.used, 2)
        self.assertEqual(self.st.launched_drones.total, 6)
        char_holder.attributes[Attribute.max_active_drones] = 4
        self.untrack_holder(holder1)
        self.assertEqual(self.st.launched_drones.used, 2)
        self.assertEqual(self.st.launched_drones.total, 6)
        self.set_character(None)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_volatility(self):
        char_item = self.ch.type_(type_id=1)
        char_holder = Mock(state=State.offline, item=char_item, _domain=None, spec_set=Character(1))
        char_holder.attributes = {Attribute.max_active_drones: 6}
        self.set_character(char_holder)
        item = self.ch.type_(type_id=2, attributes={})
        holder1 = Mock(state=State.online, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder2 = Mock(state=State.online, item=item, _domain=Domain.space, spec_set=Drone(1))
        self.track_holder(holder1)
        self.track_holder(holder2)
        self.assertEqual(self.st.launched_drones.used, 2)
        self.assertEqual(self.st.launched_drones.total, 6)
        char_holder.attributes[Attribute.max_active_drones] = 4
        self.untrack_holder(holder1)
        self.st._clear_volatile_attrs()
        self.assertEqual(self.st.launched_drones.used, 1)
        self.assertEqual(self.st.launched_drones.total, 4)
        self.set_character(None)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()
