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

from eos.const.eos import Domain, Slot, State
from eos.const.eve import Attribute
from eos.fit.holder.item import ModuleHigh, Ship
from tests.stat_tracker.stat_testcase import StatTestCase


class TestLauncherSlot(StatTestCase):

    def test_output(self):
        # Check that modified attribute of ship is used
        ship_item = self.ch.type_(type_id=1, attributes={Attribute.launcher_slots_left: 2})
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        ship_holder.attributes = {Attribute.launcher_slots_left: 6}
        self.set_ship(ship_holder)
        self.assertEqual(self.st.launcher_slots.total, 6)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_output_no_ship(self):
        # None for slot amount when no ship
        self.assertIsNone(self.st.launcher_slots.total)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_output_no_attr(self):
        # None for slot amount when no attribute on ship
        ship_item = self.ch.type_(type_id=1)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        ship_holder.attributes = {}
        self.set_ship(ship_holder)
        self.assertIsNone(self.st.launcher_slots.total)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_empty(self):
        self.assertEqual(self.st.launcher_slots.used, 0)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_single(self):
        item = self.ch.type_(type_id=1, attributes={})
        item.slots = {Slot.launcher}
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        self.assertEqual(self.st.launcher_slots.used, 1)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_other_slot(self):
        item = self.ch.type_(type_id=1, attributes={})
        item.slots = {Slot.turret}
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        self.assertEqual(self.st.launcher_slots.used, 0)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_multiple(self):
        item = self.ch.type_(type_id=1, attributes={})
        item.slots = {Slot.launcher}
        holder1 = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder2 = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder1)
        self.track_holder(holder2)
        self.assertEqual(self.st.launcher_slots.used, 2)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_mixed(self):
        item1 = self.ch.type_(type_id=1, attributes={})
        item1.slots = {Slot.launcher}
        holder1 = Mock(state=State.offline, item=item1, _domain=Domain.ship, spec_set=ModuleHigh(1))
        item2 = self.ch.type_(type_id=2, attributes={})
        item2.slots = {Slot.turret}
        holder2 = Mock(state=State.offline, item=item2, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder1)
        self.track_holder(holder2)
        self.assertEqual(self.st.launcher_slots.used, 1)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_cache(self):
        ship_item = self.ch.type_(type_id=1)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        ship_holder.attributes = {Attribute.launcher_slots_left: 6}
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=2, attributes={})
        item.slots = {Slot.launcher}
        holder1 = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder2 = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder1)
        self.track_holder(holder2)
        self.assertEqual(self.st.launcher_slots.used, 2)
        self.assertEqual(self.st.launcher_slots.total, 6)
        ship_holder.attributes[Attribute.launcher_slots_left] = 4
        self.untrack_holder(holder1)
        self.assertEqual(self.st.launcher_slots.used, 2)
        self.assertEqual(self.st.launcher_slots.total, 6)
        self.set_ship(None)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_volatility(self):
        ship_item = self.ch.type_(type_id=1)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        ship_holder.attributes = {Attribute.launcher_slots_left: 6}
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=2, attributes={})
        item.slots = {Slot.launcher}
        holder1 = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder2 = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder1)
        self.track_holder(holder2)
        self.assertEqual(self.st.launcher_slots.used, 2)
        self.assertEqual(self.st.launcher_slots.total, 6)
        ship_holder.attributes[Attribute.launcher_slots_left] = 4
        self.untrack_holder(holder1)
        self.st._clear_volatile_attrs()
        self.assertEqual(self.st.launcher_slots.used, 1)
        self.assertEqual(self.st.launcher_slots.total, 4)
        self.set_ship(None)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()
