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


from eos.const.eos import Slot, State
from eos.const.eve import Attribute
from eos.fit.item import ModuleHigh, Ship
from tests.stats.stat_testcase import StatTestCase


class TestLauncherSlot(StatTestCase):

    def test_output(self):
        # Check that modified attribute of ship is used
        ship_eve_type = self.ch.type(type_id=1, attributes={Attribute.launcher_slots_left: 2})
        ship_holder = self.make_item_mock(Ship, ship_eve_type)
        ship_holder.attributes = {Attribute.launcher_slots_left: 6}
        self.set_ship(ship_holder)
        self.assertEqual(self.ss.launcher_slots.total, 6)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_output_no_ship(self):
        # None for slot amount when no ship
        self.assertIsNone(self.ss.launcher_slots.total)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_output_no_attr(self):
        # None for slot amount when no attribute on ship
        ship_eve_type = self.ch.type(type_id=1)
        ship_holder = self.make_item_mock(Ship, ship_eve_type)
        ship_holder.attributes = {}
        self.set_ship(ship_holder)
        self.assertIsNone(self.ss.launcher_slots.total)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_empty(self):
        self.assertEqual(self.ss.launcher_slots.used, 0)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_single(self):
        eve_type = self.ch.type(type_id=1, attributes={})
        eve_type.slots = {Slot.launcher}
        holder = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        self.add_holder(holder)
        self.assertEqual(self.ss.launcher_slots.used, 1)
        self.remove_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_other_slot(self):
        eve_type = self.ch.type(type_id=1, attributes={})
        eve_type.slots = {Slot.turret}
        holder = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        self.add_holder(holder)
        self.assertEqual(self.ss.launcher_slots.used, 0)
        self.remove_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_multiple(self):
        eve_type = self.ch.type(type_id=1, attributes={})
        eve_type.slots = {Slot.launcher}
        holder1 = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        holder2 = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        self.add_holder(holder1)
        self.add_holder(holder2)
        self.assertEqual(self.ss.launcher_slots.used, 2)
        self.remove_holder(holder1)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_mixed(self):
        eve_type1 = self.ch.type(type_id=1, attributes={})
        eve_type1.slots = {Slot.launcher}
        holder1 = self.make_item_mock(ModuleHigh, eve_type1, state=State.offline)
        eve_type2 = self.ch.type(type_id=2, attributes={})
        eve_type2.slots = {Slot.turret}
        holder2 = self.make_item_mock(ModuleHigh, eve_type2, state=State.offline)
        self.add_holder(holder1)
        self.add_holder(holder2)
        self.assertEqual(self.ss.launcher_slots.used, 1)
        self.remove_holder(holder1)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_cache(self):
        ship_eve_type = self.ch.type(type_id=1)
        ship_holder = self.make_item_mock(Ship, ship_eve_type)
        ship_holder.attributes = {Attribute.launcher_slots_left: 6}
        self.set_ship(ship_holder)
        eve_type = self.ch.type(type_id=2, attributes={})
        eve_type.slots = {Slot.launcher}
        holder1 = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        holder2 = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        self.add_holder(holder1)
        self.add_holder(holder2)
        self.assertEqual(self.ss.launcher_slots.used, 2)
        self.assertEqual(self.ss.launcher_slots.total, 6)
        ship_holder.attributes[Attribute.launcher_slots_left] = 4
        self.remove_holder(holder1)
        self.assertEqual(self.ss.launcher_slots.used, 2)
        self.assertEqual(self.ss.launcher_slots.total, 6)
        self.set_ship(None)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_volatility(self):
        ship_eve_type = self.ch.type(type_id=1)
        ship_holder = self.make_item_mock(Ship, ship_eve_type)
        ship_holder.attributes = {Attribute.launcher_slots_left: 6}
        self.set_ship(ship_holder)
        eve_type = self.ch.type(type_id=2, attributes={})
        eve_type.slots = {Slot.launcher}
        holder1 = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        holder2 = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        self.add_holder(holder1)
        self.add_holder(holder2)
        self.assertEqual(self.ss.launcher_slots.used, 2)
        self.assertEqual(self.ss.launcher_slots.total, 6)
        ship_holder.attributes[Attribute.launcher_slots_left] = 4
        self.remove_holder(holder1)
        self.ss._clear_volatile_attrs()
        self.assertEqual(self.ss.launcher_slots.used, 1)
        self.assertEqual(self.ss.launcher_slots.total, 4)
        self.set_ship(None)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()
