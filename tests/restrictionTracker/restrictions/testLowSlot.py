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

from eos.const.eos import Location, Restriction, Slot, State
from eos.const.eve import Attribute
from eos.fit.holder.item import Module, Ship
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestLowSlot(RestrictionTestCase):
    """Check functionality of low slot amount restriction"""

    def testFail(self):
        # Check that error is raised when number of used
        # slots exceeds slot amount provided by ship
        item = self.ch.type_(typeId=1)
        item.slots = {Slot.moduleLow}
        holder1 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder1)
        holder2 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder2)
        shipItem = self.ch.type_(typeId=2)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {Attribute.lowSlots: 1}
        self.setShip(shipHolder)
        restrictionError1 = self.getRestrictionError(holder1, Restriction.lowSlot)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.slotsMax, 1)
        self.assertEqual(restrictionError1.slotsUsed, 2)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.lowSlot)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.slotsMax, 1)
        self.assertEqual(restrictionError2.slotsUsed, 2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailShipNoAttr(self):
        # Make sure that absence of specifier of slot output
        # is considered as 0 output
        item = self.ch.type_(typeId=1)
        item.slots = {Slot.moduleLow}
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        shipItem = self.ch.type_(typeId=2)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {}
        self.setShip(shipHolder)
        restrictionError = self.getRestrictionError(holder, Restriction.lowSlot)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.slotsMax, 0)
        self.assertEqual(restrictionError.slotsUsed, 1)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailNoShip(self):
        # Make sure that absence of ship
        # is considered as 0 output
        item = self.ch.type_(typeId=1)
        item.slots = {Slot.moduleLow}
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.lowSlot)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.slotsMax, 0)
        self.assertEqual(restrictionError.slotsUsed, 1)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailModified(self):
        # Make sure that modified number of slot output
        # is taken
        item = self.ch.type_(typeId=1)
        item.slots = {Slot.moduleLow}
        holder1 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder1)
        holder2 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder2)
        shipItem = self.ch.type_(typeId=2, attributes={Attribute.lowSlots: 5})
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {Attribute.lowSlots: 1}
        self.setShip(shipHolder)
        restrictionError1 = self.getRestrictionError(holder1, Restriction.lowSlot)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.slotsMax, 1)
        self.assertEqual(restrictionError1.slotsUsed, 2)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.lowSlot)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.slotsMax, 1)
        self.assertEqual(restrictionError2.slotsUsed, 2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPass(self):
        # No error is raised when slot users do not
        # exceed slot output
        item = self.ch.type_(typeId=1)
        item.slots = {Slot.moduleLow}
        holder1 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder1)
        holder2 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder2)
        shipItem = self.ch.type_(typeId=2)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {Attribute.lowSlots: 3}
        self.setShip(shipHolder)
        restrictionError1 = self.getRestrictionError(holder1, Restriction.lowSlot)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.lowSlot)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassHolderNonShip(self):
        # Non-ship holders shouldn't be affected
        item = self.ch.type_(typeId=1)
        item.slots = {Slot.moduleLow}
        holder1 = Mock(state=State.offline, item=item, _location=None, spec_set=Module)
        self.trackHolder(holder1)
        holder2 = Mock(state=State.offline, item=item, _location=None, spec_set=Module)
        self.trackHolder(holder2)
        shipItem = self.ch.type_(typeId=2)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {Attribute.lowSlots: 1}
        self.setShip(shipHolder)
        restrictionError1 = self.getRestrictionError(holder1, Restriction.lowSlot)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.lowSlot)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassNonSlot(self):
        # If holders don't use slot, no error should
        # be raised
        item = self.ch.type_(typeId=1)
        item.slots = set()
        holder1 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder1)
        holder2 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder2)
        shipItem = self.ch.type_(typeId=2)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {Attribute.lowSlots: 1}
        self.setShip(shipHolder)
        restrictionError1 = self.getRestrictionError(holder1, Restriction.lowSlot)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.lowSlot)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()
