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
from eos.fit.item import ModuleHigh, Ship
from tests.stats.stat_testcase import StatTestCase


class TestHighSlot(StatTestCase):

    def test_output(self):
        # Check that modified attribute of ship is used
        ship_eve_type = self.ch.type_(type_id=1, attributes={Attribute.hi_slots: 2})
        ship_holder = self.make_item_mock(Ship, ship_eve_type)
        ship_holder.attributes = {Attribute.hi_slots: 6}
        self.set_ship(ship_holder)
        self.assertEqual(self.ss.high_slots.total, 6)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_output_no_ship(self):
        # None for slot amount when no ship
        self.assertIsNone(self.ss.high_slots.total)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_output_no_attr(self):
        # None for slot amount when no attribute on ship
        ship_eve_type = self.ch.type_(type_id=1)
        ship_holder = self.make_item_mock(Ship, ship_eve_type)
        ship_holder.attributes = {}
        self.set_ship(ship_holder)
        self.assertIsNone(self.ss.high_slots.total)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_empty(self):
        self.assertEqual(self.ss.high_slots.used, 0)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_multiple(self):
        eve_type = self.ch.type_(type_id=1, attributes={})
        holder1 = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        holder2 = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        self.fit.modules.high.append(holder1)
        self.fit.modules.high.append(holder2)
        self.assertEqual(self.ss.high_slots.used, 2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_multiple_with_none(self):
        eve_type = self.ch.type_(type_id=1, attributes={})
        holder1 = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        holder2 = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        self.fit.modules.high.append(None)
        self.fit.modules.high.append(holder1)
        self.fit.modules.high.append(None)
        self.fit.modules.high.append(holder2)
        self.assertEqual(self.ss.high_slots.used, 4)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_other_container(self):
        eve_type = self.ch.type_(type_id=1, attributes={})
        holder = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        self.fit.modules.med.append(holder)
        self.assertEqual(self.ss.high_slots.used, 0)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_cache(self):
        ship_eve_type = self.ch.type_(type_id=1)
        ship_holder = self.make_item_mock(Ship, ship_eve_type)
        ship_holder.attributes = {Attribute.hi_slots: 6}
        self.set_ship(ship_holder)
        eve_type = self.ch.type_(type_id=2, attributes={})
        holder1 = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        holder2 = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        self.fit.modules.high.append(holder1)
        self.fit.modules.high.append(holder2)
        self.assertEqual(self.ss.high_slots.used, 2)
        self.assertEqual(self.ss.high_slots.total, 6)
        ship_holder.attributes[Attribute.hi_slots] = 4
        self.fit.modules.high.remove(holder1)
        self.assertEqual(self.ss.high_slots.used, 2)
        self.assertEqual(self.ss.high_slots.total, 6)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_volatility(self):
        ship_eve_type = self.ch.type_(type_id=1)
        ship_holder = self.make_item_mock(Ship, ship_eve_type)
        ship_holder.attributes = {Attribute.hi_slots: 6}
        self.set_ship(ship_holder)
        eve_type = self.ch.type_(type_id=2, attributes={})
        holder1 = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        holder2 = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        self.fit.modules.high.append(holder1)
        self.fit.modules.high.append(holder2)
        self.assertEqual(self.ss.high_slots.used, 2)
        self.assertEqual(self.ss.high_slots.total, 6)
        ship_holder.attributes[Attribute.hi_slots] = 4
        self.fit.modules.high.remove(holder1)
        self.ss._clear_volatile_attrs()
        self.assertEqual(self.ss.high_slots.used, 1)
        self.assertEqual(self.ss.high_slots.total, 4)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()
