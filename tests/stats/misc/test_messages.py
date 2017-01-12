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

from eos.const.eos import Domain, State
from eos.const.eve import Attribute
from eos.fit.holder.item import ModuleHigh
from eos.fit.messages import HolderAdded, HolderRemoved, HolderStateChanged, EnableServices, DisableServices
from tests.stats.stat_testcase import StatTestCase


class TestMessages(StatTestCase):
    """Check how service handles messages"""

    def test_add_stateless(self):
        # Check that when holder is added w/o enabling any states,
        # it's added to corresponding registers
        # Setup
        item = self.ch.type_(type_id=1, attributes={Attribute.upgrade_cost: 0})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder.attributes = {Attribute.upgrade_cost: 33}
        # Action
        self.ss._notify(HolderAdded(holder))
        # Checks
        self.assertEqual(self.ss.calibration.used, 33)
        # Misc
        self.ss._notify(HolderRemoved(holder))
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_add_stateful(self):
        # Setup
        item = self.ch.type_(type_id=1, attributes={Attribute.cpu: 0})
        holder = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder.attributes = {Attribute.cpu: 35}
        # Action
        self.ss._notify(HolderAdded(holder))
        # Checks
        self.assertEqual(self.ss.cpu.used, 35)
        # Misc
        self.ss._notify(HolderRemoved(holder))
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_add_stateful_insufficient(self):
        # Setup
        item = self.ch.type_(type_id=1, attributes={Attribute.cpu: 0})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder.attributes = {Attribute.cpu: 35}
        # Action
        self.ss._notify(HolderAdded(holder))
        # Checks
        self.assertEqual(self.ss.cpu.used, 0)
        # Misc
        self.ss._notify(HolderRemoved(holder))
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_remove_stateless(self):
        # Setup
        item = self.ch.type_(type_id=1, attributes={Attribute.upgrade_cost: 0})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder.attributes = {Attribute.upgrade_cost: 33}
        self.ss._notify(HolderAdded(holder))
        # Action
        self.ss._notify(HolderRemoved(holder))
        # Checks
        self.assertEqual(self.ss.calibration.used, 0)
        # Misc
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_remove_stateful(self):
        # Setup
        item = self.ch.type_(type_id=1, attributes={Attribute.cpu: 0})
        holder = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder.attributes = {Attribute.cpu: 35}
        self.ss._notify(HolderAdded(holder))
        # Action
        self.ss._notify(HolderRemoved(holder))
        # Checks
        self.assertEqual(self.ss.cpu.used, 0)
        # Misc
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_state_switch_up(self):
        # Setup
        item = self.ch.type_(type_id=1, attributes={Attribute.cpu: 0})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder.attributes = {Attribute.cpu: 35}
        self.ss._notify(HolderAdded(holder))
        # Action
        self.ss._notify(HolderStateChanged(holder, State.offline, State.online))
        holder.state = State.online
        # Checks
        self.assertEqual(self.ss.cpu.used, 35)
        # Misc
        self.ss._notify(HolderRemoved(holder))
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_state_switch_down(self):
        # Setup
        item = self.ch.type_(type_id=1, attributes={Attribute.cpu: 0})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder.attributes = {Attribute.cpu: 35}
        self.ss._notify(HolderAdded(holder))
        self.ss._notify(HolderStateChanged(holder, State.offline, State.online))
        holder.state = State.online
        # Action
        self.ss._notify(HolderStateChanged(holder, State.online, State.offline))
        holder.state = State.offline
        # Checks
        self.assertEqual(self.ss.cpu.used, 0)
        # Misc
        self.ss._notify(HolderRemoved(holder))
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_add_stateful_disabled(self):
        # Check that service takes holder which was added
        # while service was disabled into consideration
        # Setup
        item = self.ch.type_(type_id=1, attributes={Attribute.cpu: 0})
        holder = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder.attributes = {Attribute.cpu: 35}
        self.ss._notify(DisableServices(holders=(holder,)))
        # Action
        self.ss._notify(HolderAdded(holder))
        self.ss._notify(EnableServices(holders=(holder,)))
        # Checks
        self.assertEqual(self.ss.cpu.used, 35)
        # Misc
        self.ss._notify(HolderRemoved(holder))
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_remove_stateful_disabled(self):
        # Setup
        item = self.ch.type_(type_id=1, attributes={Attribute.cpu: 0})
        holder = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder.attributes = {Attribute.cpu: 35}
        self.ss._notify(HolderAdded(holder))
        # Action
        self.ss._notify(DisableServices(holders=(holder,)))
        # Checks
        self.assertEqual(self.ss.cpu.used, 0)
        # Misc
        self.ss._notify(HolderRemoved(holder))
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()
