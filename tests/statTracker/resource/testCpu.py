#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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
#===============================================================================


from unittest.mock import Mock

from eos.const.eos import Location, State
from eos.const.eve import Attribute
from eos.fit.holder.item import Module, Ship, Implant
from eos.tests.statTracker.statTestCase import StatTestCase


class TestCpu(StatTestCase):
    """Check functionality of cpu stats"""

    def testOutput(self):
        # Check that modified attribute of ship is used
        shipItem = self.ch.type_(typeId=1, attributes={Attribute.cpuOutput: 10})
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {Attribute.cpuOutput: 50}
        self.setShip(shipHolder)
        self.assertEqual(self.st.cpu.output, 50)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testOutputNoShip(self):
        # None for output when no ship
        self.assertIsNone(self.st.cpu.output)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testOutputNoAttr(self):
        # None for output when no attribute on ship
        shipItem = self.ch.type_(typeId=1)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {}
        self.setShip(shipHolder)
        self.assertIsNone(self.st.cpu.output)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseSingle(self):
        item = self.ch.type_(typeId=1, attributes={Attribute.cpu: 0})
        holder = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder.attributes = {Attribute.cpu: 50}
        self.trackHolder(holder)
        self.assertEqual(self.st.cpu.used, 50)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseMultiple(self):
        item = self.ch.type_(typeId=1, attributes={Attribute.cpu: 0})
        holder1 = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder1.attributes = {Attribute.cpu: 50}
        self.trackHolder(holder1)
        holder2 = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder2.attributes = {Attribute.cpu: 30}
        self.trackHolder(holder2)
        self.assertEqual(self.st.cpu.used, 80)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseNegative(self):
        item = self.ch.type_(typeId=1, attributes={Attribute.cpu: 0})
        holder1 = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder1.attributes = {Attribute.cpu: 50}
        self.trackHolder(holder1)
        holder2 = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder2.attributes = {Attribute.cpu: -30}
        self.trackHolder(holder2)
        self.assertEqual(self.st.cpu.used, 20)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseNone(self):
        self.assertEqual(self.st.cpu.used, 0)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseState(self):
        item = self.ch.type_(typeId=1, attributes={Attribute.cpu: 0})
        holder1 = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder1.attributes = {Attribute.cpu: 50}
        self.trackHolder(holder1)
        holder2 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        holder2.attributes = {Attribute.cpu: 30}
        self.trackHolder(holder2)
        self.assertEqual(self.st.cpu.used, 50)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseOtherClassLocation(self):
        item = self.ch.type_(typeId=1, attributes={Attribute.cpu: 0})
        holder1 = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder1.attributes = {Attribute.cpu: 50}
        self.trackHolder(holder1)
        holder2 = Mock(state=State.online, item=item, _location=Location.character, spec_set=Implant)
        holder2.attributes = {Attribute.cpu: 30}
        self.trackHolder(holder2)
        self.assertEqual(self.st.cpu.used, 80)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()
