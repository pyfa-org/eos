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

from eos.const.eos import ModifierDomain, State
from eos.const.eve import Attribute
from eos.fit.item import ModuleHigh, Ship, Implant
from tests.stats.stat_testcase import StatTestCase


class TestCalibration(StatTestCase):
    """Check functionality of calibration stats"""

    def test_output(self):
        # Check that modified attribute of ship is used
        ship_item = self.ch.type_(type_id=1, attributes={Attribute.upgrade_capacity: 10})
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        ship_holder.attributes = {Attribute.upgrade_capacity: 50}
        self.set_ship(ship_holder)
        self.assertEqual(self.ss.calibration.output, 50)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_output_no_ship(self):
        # None for output when no ship
        self.assertIsNone(self.ss.calibration.output)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_output_no_attr(self):
        # None for output when no attribute on ship
        ship_item = self.ch.type_(type_id=1)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        ship_holder.attributes = {}
        self.set_ship(ship_holder)
        self.assertIsNone(self.ss.calibration.output)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_single_no_rounding(self):
        item = self.ch.type_(type_id=1, attributes={Attribute.upgrade_cost: 0})
        holder = Mock(state=State.offline, item=item, _domain=ModifierDomain.ship, spec_set=ModuleHigh(1))
        holder.attributes = {Attribute.upgrade_cost: 55.5555555555}
        self.add_holder(holder)
        self.assertEqual(self.ss.calibration.used, 55.5555555555)
        self.remove_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_multiple(self):
        item = self.ch.type_(type_id=1, attributes={Attribute.upgrade_cost: 0})
        holder1 = Mock(state=State.offline, item=item, _domain=ModifierDomain.ship, spec_set=ModuleHigh(1))
        holder1.attributes = {Attribute.upgrade_cost: 50}
        self.add_holder(holder1)
        holder2 = Mock(state=State.offline, item=item, _domain=ModifierDomain.ship, spec_set=ModuleHigh(1))
        holder2.attributes = {Attribute.upgrade_cost: 30}
        self.add_holder(holder2)
        self.assertEqual(self.ss.calibration.used, 80)
        self.remove_holder(holder1)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_negative(self):
        item = self.ch.type_(type_id=1, attributes={Attribute.upgrade_cost: 0})
        holder1 = Mock(state=State.offline, item=item, _domain=ModifierDomain.ship, spec_set=ModuleHigh(1))
        holder1.attributes = {Attribute.upgrade_cost: 50}
        self.add_holder(holder1)
        holder2 = Mock(state=State.offline, item=item, _domain=ModifierDomain.ship, spec_set=ModuleHigh(1))
        holder2.attributes = {Attribute.upgrade_cost: -30}
        self.add_holder(holder2)
        self.assertEqual(self.ss.calibration.used, 20)
        self.remove_holder(holder1)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_none(self):
        self.assertEqual(self.ss.calibration.used, 0)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_other_class_domain(self):
        item = self.ch.type_(type_id=1, attributes={Attribute.upgrade_cost: 0})
        holder1 = Mock(state=State.offline, item=item, _domain=ModifierDomain.ship, spec_set=ModuleHigh(1))
        holder1.attributes = {Attribute.upgrade_cost: 50}
        self.add_holder(holder1)
        holder2 = Mock(state=State.offline, item=item, _domain=ModifierDomain.character, spec_set=Implant(1))
        holder2.attributes = {Attribute.upgrade_cost: 30}
        self.add_holder(holder2)
        self.assertEqual(self.ss.calibration.used, 80)
        self.remove_holder(holder1)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_cache(self):
        ship_item = self.ch.type_(type_id=1, attributes={Attribute.upgrade_capacity: 10})
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        ship_holder.attributes = {Attribute.upgrade_capacity: 50}
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=2, attributes={Attribute.upgrade_cost: 0})
        holder1 = Mock(state=State.online, item=item, _domain=ModifierDomain.ship, spec_set=ModuleHigh(1))
        holder1.attributes = {Attribute.upgrade_cost: 50}
        self.add_holder(holder1)
        holder2 = Mock(state=State.online, item=item, _domain=ModifierDomain.ship, spec_set=ModuleHigh(1))
        holder2.attributes = {Attribute.upgrade_cost: 30}
        self.add_holder(holder2)
        self.assertEqual(self.ss.calibration.used, 80)
        self.assertEqual(self.ss.calibration.output, 50)
        holder1.attributes[Attribute.upgrade_cost] = 10
        ship_holder.attributes[Attribute.upgrade_capacity] = 60
        self.assertEqual(self.ss.calibration.used, 80)
        self.assertEqual(self.ss.calibration.output, 50)
        self.set_ship(None)
        self.remove_holder(holder1)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_volatility(self):
        ship_item = self.ch.type_(type_id=1, attributes={Attribute.upgrade_capacity: 10})
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        ship_holder.attributes = {Attribute.upgrade_capacity: 50}
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=2, attributes={Attribute.upgrade_cost: 0})
        holder1 = Mock(state=State.online, item=item, _domain=ModifierDomain.ship, spec_set=ModuleHigh(1))
        holder1.attributes = {Attribute.upgrade_cost: 50}
        self.add_holder(holder1)
        holder2 = Mock(state=State.online, item=item, _domain=ModifierDomain.ship, spec_set=ModuleHigh(1))
        holder2.attributes = {Attribute.upgrade_cost: 30}
        self.add_holder(holder2)
        self.assertEqual(self.ss.calibration.used, 80)
        self.assertEqual(self.ss.calibration.output, 50)
        holder1.attributes[Attribute.upgrade_cost] = 10
        ship_holder.attributes[Attribute.upgrade_capacity] = 60
        self.ss._clear_volatile_attrs()
        self.assertEqual(self.ss.calibration.used, 40)
        self.assertEqual(self.ss.calibration.output, 60)
        self.set_ship(None)
        self.remove_holder(holder1)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()
