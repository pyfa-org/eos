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

from eos.const.eos import ModifierDomain, Restriction, State
from eos.const.eve import Attribute
from eos.fit.item import ModuleHigh, Rig
from eos.fit.messages import HolderAdded, HolderRemoved, HolderStateChanged, EnableServices, DisableServices
from tests.restrictions.restriction_testcase import RestrictionTestCase


class TestMessages(RestrictionTestCase):
    """Check how service handles messages"""

    def test_add_stateless(self):
        # Check that when holder is added w/o enabling any states,
        # it's added to corresponding registers
        # Setup
        eve_type = self.ch.type_(type_id=1, attributes={Attribute.upgrade_cost: 0})
        holder = self.make_item_mock(Rig, eve_type)
        holder.attributes = {Attribute.upgrade_cost: 50}
        self.fit.stats.calibration.used = 50
        self.fit.stats.calibration.output = 40
        # Action
        self.rs._notify(HolderAdded(holder))
        # Checks
        restriction_error = self.get_restriction_error(holder, Restriction.calibration)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 40)
        self.assertEqual(restriction_error.total_use, 50)
        self.assertEqual(restriction_error.holder_use, 50)
        # Misc
        self.rs._notify(HolderRemoved(holder))
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_add_stateful(self):
        # Setup
        eve_type = self.ch.type_(type_id=1, attributes={Attribute.cpu: 0})
        holder = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder.attributes = {Attribute.cpu: 50}
        self.fit.stats.cpu.used = 50
        self.fit.stats.cpu.output = 40
        # Action
        self.rs._notify(HolderAdded(holder))
        # Checks
        restriction_error = self.get_restriction_error(holder, Restriction.cpu)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 40)
        self.assertEqual(restriction_error.total_use, 50)
        self.assertEqual(restriction_error.holder_use, 50)
        # Misc
        self.rs._notify(HolderRemoved(holder))
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_add_stateful_insufficient(self):
        # Setup
        eve_type = self.ch.type_(type_id=1, attributes={Attribute.cpu: 0})
        holder = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        holder.attributes = {Attribute.cpu: 50}
        self.fit.stats.cpu.used = 50
        self.fit.stats.cpu.output = 40
        # Action
        self.rs._notify(HolderAdded(holder))
        # Checks
        restriction_error = self.get_restriction_error(holder, Restriction.cpu)
        self.assertIsNone(restriction_error)
        # Misc
        self.rs._notify(HolderRemoved(holder))
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_remove_stateless(self):
        # Setup
        eve_type = self.ch.type_(type_id=1, attributes={Attribute.upgrade_cost: 0})
        holder = self.make_item_mock(Rig, eve_type)
        holder.attributes = {Attribute.upgrade_cost: 50}
        self.fit.stats.calibration.used = 50
        self.fit.stats.calibration.output = 40
        self.rs._notify(HolderAdded(holder))
        # Action
        self.rs._notify(HolderRemoved(holder))
        # Checks
        restriction_error = self.get_restriction_error(holder, Restriction.calibration)
        self.assertIsNone(restriction_error)
        # Misc
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_remove_stateful(self):
        # Setup
        eve_type = self.ch.type_(type_id=1, attributes={Attribute.cpu: 0})
        holder = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder.attributes = {Attribute.cpu: 50}
        self.fit.stats.cpu.used = 50
        self.fit.stats.cpu.output = 40
        self.rs._notify(HolderAdded(holder))
        # Action
        self.rs._notify(HolderRemoved(holder))
        # Checks
        restriction_error = self.get_restriction_error(holder, Restriction.cpu)
        self.assertIsNone(restriction_error)
        # Misc
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_state_switch_up(self):
        # Setup
        eve_type = self.ch.type_(type_id=1, attributes={Attribute.cpu: 0})
        holder = self.make_item_mock(ModuleHigh, eve_type, state=State.offline)
        holder.attributes = {Attribute.cpu: 50}
        self.fit.stats.cpu.used = 50
        self.fit.stats.cpu.output = 40
        self.rs._notify(HolderAdded(holder))
        # Action
        self.rs._notify(HolderStateChanged(holder, State.offline, State.online))
        holder.state = State.online
        # Checks
        restriction_error = self.get_restriction_error(holder, Restriction.cpu)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 40)
        self.assertEqual(restriction_error.total_use, 50)
        self.assertEqual(restriction_error.holder_use, 50)
        # Misc
        self.rs._notify(HolderRemoved(holder))
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_state_switch_down(self):
        # Setup
        eve_type = self.ch.type_(type_id=1, attributes={Attribute.cpu: 0})
        holder = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder.attributes = {Attribute.cpu: 50}
        self.fit.stats.cpu.used = 50
        self.fit.stats.cpu.output = 40
        self.rs._notify(HolderAdded(holder))
        # Action
        self.rs._notify(HolderStateChanged(holder, State.online, State.offline))
        holder.state = State.offline
        # Checks
        restriction_error = self.get_restriction_error(holder, Restriction.cpu)
        self.assertIsNone(restriction_error)
        # Misc
        self.rs._notify(HolderRemoved(holder))
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_add_stateful_disabled(self):
        # Check that service takes holder which was added
        # while service was disabled into consideration
        # Setup
        eve_type = self.ch.type_(type_id=1, attributes={Attribute.cpu: 0})
        holder = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder.attributes = {Attribute.cpu: 50}
        self.fit.stats.cpu.used = 50
        self.fit.stats.cpu.output = 40
        self.rs._notify(DisableServices(holders=(holder,)))
        # Action
        self.rs._notify(HolderAdded(holder))
        self.rs._notify(EnableServices(holders=(holder,)))
        # Checks
        restriction_error = self.get_restriction_error(holder, Restriction.cpu)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 40)
        self.assertEqual(restriction_error.total_use, 50)
        self.assertEqual(restriction_error.holder_use, 50)
        # Misc
        self.rs._notify(HolderRemoved(holder))
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_remove_stateful_disabled(self):
        # Setup
        eve_type = self.ch.type_(type_id=1, attributes={Attribute.cpu: 0})
        holder = self.make_item_mock(ModuleHigh, eve_type, state=State.online)
        holder.attributes = {Attribute.cpu: 50}
        self.fit.stats.cpu.used = 50
        self.fit.stats.cpu.output = 40
        self.rs._notify(HolderAdded(holder))
        # Action
        self.rs._notify(DisableServices(holders=(holder,)))
        # Checks
        restriction_error = self.get_restriction_error(holder, Restriction.cpu)
        self.assertIsNone(restriction_error)
        # Misc
        self.rs._notify(HolderRemoved(holder))
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()
