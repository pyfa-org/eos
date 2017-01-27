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
from eos.fit.item import ModuleHigh
from eos.fit.messages import ItemAdded, ItemRemoved, ItemStateChanged, EnableServices, DisableServices
from tests.stats.stat_testcase import StatTestCase


class TestMessages(StatTestCase):
    """Check how service handles messages"""

    def test_add_stateless(self):
        # Check that when item is added w/o enabling any states,
        # it's added to corresponding registers
        # Setup
        eve_type = self.ch.type(type_id=1, attributes={Attribute.upgrade_cost: 0})
        item = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        item.attributes = {Attribute.upgrade_cost: 33}
        # Action
        self.ss._notify(ItemAdded(item))
        # Checks
        self.assertEqual(self.ss.calibration.used, 33)
        # Misc
        self.ss._notify(ItemRemoved(item))
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_add_stateful(self):
        # Setup
        eve_type = self.ch.type(type_id=1, attributes={Attribute.cpu: 0})
        item = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        item.attributes = {Attribute.cpu: 35}
        # Action
        self.ss._notify(ItemAdded(item))
        # Checks
        self.assertEqual(self.ss.cpu.used, 35)
        # Misc
        self.ss._notify(ItemRemoved(item))
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_add_stateful_insufficient(self):
        # Setup
        eve_type = self.ch.type(type_id=1, attributes={Attribute.cpu: 0})
        item = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        item.attributes = {Attribute.cpu: 35}
        # Action
        self.ss._notify(ItemAdded(item))
        # Checks
        self.assertEqual(self.ss.cpu.used, 0)
        # Misc
        self.ss._notify(ItemRemoved(item))
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_remove_stateless(self):
        # Setup
        eve_type = self.ch.type(type_id=1, attributes={Attribute.upgrade_cost: 0})
        item = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        item.attributes = {Attribute.upgrade_cost: 33}
        self.ss._notify(ItemAdded(item))
        # Action
        self.ss._notify(ItemRemoved(item))
        # Checks
        self.assertEqual(self.ss.calibration.used, 0)
        # Misc
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_remove_stateful(self):
        # Setup
        eve_type = self.ch.type(type_id=1, attributes={Attribute.cpu: 0})
        item = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        item.attributes = {Attribute.cpu: 35}
        self.ss._notify(ItemAdded(item))
        # Action
        self.ss._notify(ItemRemoved(item))
        # Checks
        self.assertEqual(self.ss.cpu.used, 0)
        # Misc
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_state_switch_up(self):
        # Setup
        eve_type = self.ch.type(type_id=1, attributes={Attribute.cpu: 0})
        item = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        item.attributes = {Attribute.cpu: 35}
        self.ss._notify(ItemAdded(item))
        # Action
        self.ss._notify(ItemStateChanged(item, State.offline, State.online))
        item.state = State.online
        # Checks
        self.assertEqual(self.ss.cpu.used, 35)
        # Misc
        self.ss._notify(ItemRemoved(item))
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_state_switch_down(self):
        # Setup
        eve_type = self.ch.type(type_id=1, attributes={Attribute.cpu: 0})
        item = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        item.attributes = {Attribute.cpu: 35}
        self.ss._notify(ItemAdded(item))
        self.ss._notify(ItemStateChanged(item, State.offline, State.online))
        item.state = State.online
        # Action
        self.ss._notify(ItemStateChanged(item, State.online, State.offline))
        item.state = State.offline
        # Checks
        self.assertEqual(self.ss.cpu.used, 0)
        # Misc
        self.ss._notify(ItemRemoved(item))
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_add_stateful_disabled(self):
        # Check that service takes item which was added
        # while service was disabled into consideration
        # Setup
        eve_type = self.ch.type(type_id=1, attributes={Attribute.cpu: 0})
        item = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        item.attributes = {Attribute.cpu: 35}
        self.ss._notify(DisableServices(items=(item,)))
        # Action
        self.ss._notify(ItemAdded(item))
        self.ss._notify(EnableServices(items=(item,)))
        # Checks
        self.assertEqual(self.ss.cpu.used, 35)
        # Misc
        self.ss._notify(ItemRemoved(item))
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_remove_stateful_disabled(self):
        # Setup
        eve_type = self.ch.type(type_id=1, attributes={Attribute.cpu: 0})
        item = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        item.attributes = {Attribute.cpu: 35}
        self.ss._notify(ItemAdded(item))
        # Action
        self.ss._notify(DisableServices(items=(item,)))
        # Checks
        self.assertEqual(self.ss.cpu.used, 0)
        # Misc
        self.ss._notify(ItemRemoved(item))
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()
