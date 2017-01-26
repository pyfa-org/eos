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
from eos.fit.item import ModuleHigh, Ship, Implant
from tests.stats.stat_testcase import StatTestCase


class TestPowergrid(StatTestCase):
    """Check functionality of powergrid stats"""

    def test_output(self):
        # Check that modified attribute of ship is used
        ship_eve_type = self.ch.type_(type_id=1, attributes={Attribute.power_output: 10})
        ship_holder = self.make_item_mock(Ship, ship_eve_type)
        ship_holder.attributes = {Attribute.power_output: 50}
        self.set_ship(ship_holder)
        self.assertEqual(self.ss.powergrid.output, 50)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_output_no_ship(self):
        # None for output when no ship
        self.assertIsNone(self.ss.powergrid.output)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_output_no_attr(self):
        # None for output when no attribute on ship
        ship_eve_type = self.ch.type_(type_id=1)
        ship_holder = self.make_item_mock(Ship, ship_eve_type)
        ship_holder.attributes = {}
        self.set_ship(ship_holder)
        self.assertIsNone(self.ss.powergrid.output)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_single_rounding_up(self):
        eve_type = self.ch.type_(type_id=1, attributes={Attribute.power: 0})
        holder = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder.attributes = {Attribute.power: 55.5555555555}
        self.add_holder(holder)
        self.assertEqual(self.ss.powergrid.used, 55.56)
        self.remove_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_single_rounding_down(self):
        eve_type = self.ch.type_(type_id=1, attributes={Attribute.power: 0})
        holder = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder.attributes = {Attribute.power: 44.4444444444}
        self.add_holder(holder)
        self.assertEqual(self.ss.powergrid.used, 44.44)
        self.remove_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_multiple(self):
        eve_type = self.ch.type_(type_id=1, attributes={Attribute.power: 0})
        holder1 = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder1.attributes = {Attribute.power: 50}
        self.add_holder(holder1)
        holder2 = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder2.attributes = {Attribute.power: 30}
        self.add_holder(holder2)
        self.assertEqual(self.ss.powergrid.used, 80)
        self.remove_holder(holder1)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_negative(self):
        eve_type = self.ch.type_(type_id=1, attributes={Attribute.power: 0})
        holder1 = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder1.attributes = {Attribute.power: 50}
        self.add_holder(holder1)
        holder2 = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder2.attributes = {Attribute.power: -30}
        self.add_holder(holder2)
        self.assertEqual(self.ss.powergrid.used, 20)
        self.remove_holder(holder1)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_none(self):
        self.assertEqual(self.ss.powergrid.used, 0)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_state(self):
        eve_type = self.ch.type_(type_id=1, attributes={Attribute.power: 0})
        holder1 = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder1.attributes = {Attribute.power: 50}
        self.add_holder(holder1)
        holder2 = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        holder2.attributes = {Attribute.power: 30}
        self.add_holder(holder2)
        self.assertEqual(self.ss.powergrid.used, 50)
        self.remove_holder(holder1)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_other_class_domain(self):
        eve_type = self.ch.type_(type_id=1, attributes={Attribute.power: 0})
        holder1 = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder1.attributes = {Attribute.power: 50}
        self.add_holder(holder1)
        holder2 = self.make_item_mock(Implant, eve_type, state=State.online)
        holder2.attributes = {Attribute.power: 30}
        self.add_holder(holder2)
        self.assertEqual(self.ss.powergrid.used, 80)
        self.remove_holder(holder1)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_cache(self):
        ship_eve_type = self.ch.type_(type_id=1, attributes={Attribute.power_output: 10})
        ship_holder = self.make_item_mock(Ship, ship_eve_type)
        ship_holder.attributes = {Attribute.power_output: 50}
        self.set_ship(ship_holder)
        eve_type = self.ch.type_(type_id=2, attributes={Attribute.power: 0})
        holder1 = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder1.attributes = {Attribute.power: 50}
        self.add_holder(holder1)
        holder2 = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder2.attributes = {Attribute.power: 30}
        self.add_holder(holder2)
        self.assertEqual(self.ss.powergrid.used, 80)
        self.assertEqual(self.ss.powergrid.output, 50)
        holder1.attributes[Attribute.power] = 10
        ship_holder.attributes[Attribute.power_output] = 60
        self.assertEqual(self.ss.powergrid.used, 80)
        self.assertEqual(self.ss.powergrid.output, 50)
        self.set_ship(None)
        self.remove_holder(holder1)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_volatility(self):
        ship_eve_type = self.ch.type_(type_id=1, attributes={Attribute.power_output: 10})
        ship_holder = self.make_item_mock(Ship, ship_eve_type)
        ship_holder.attributes = {Attribute.power_output: 50}
        self.set_ship(ship_holder)
        eve_type = self.ch.type_(type_id=2, attributes={Attribute.power: 0})
        holder1 = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder1.attributes = {Attribute.power: 50}
        self.add_holder(holder1)
        holder2 = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder2.attributes = {Attribute.power: 30}
        self.add_holder(holder2)
        self.assertEqual(self.ss.powergrid.used, 80)
        self.assertEqual(self.ss.powergrid.output, 50)
        holder1.attributes[Attribute.power] = 10
        ship_holder.attributes[Attribute.power_output] = 60
        self.ss._clear_volatile_attrs()
        self.assertEqual(self.ss.powergrid.used, 40)
        self.assertEqual(self.ss.powergrid.output, 60)
        self.set_ship(None)
        self.remove_holder(holder1)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()
