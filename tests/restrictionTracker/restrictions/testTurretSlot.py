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
from eos.fit.holder.item import Implant, Module
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestTurretSlot(RestrictionTestCase):
    """Check functionality of turret slot amount restriction"""

    def testFailExcessSignle(self):
        # Check that error is raised when number of used
        # slots exceeds slot amount provided by ship
        item = self.ch.type_(typeId=1)
        item.slots = {Slot.turret}
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        self.fit.stats.turretSlots.used = 1
        self.fit.stats.turretSlots.total = 0
        restrictionError = self.getRestrictionError(holder, Restriction.turretSlot)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.slotsMaxAllowed, 0)
        self.assertEqual(restrictionError.slotsUsed, 1)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailExcessSignleOtherClassLocation(self):
        # Make sure holders of all classes are affected
        item = self.ch.type_(typeId=1)
        item.slots = {Slot.turret}
        holder = Mock(state=State.offline, item=item, _location=Location.character, spec_set=Implant)
        self.trackHolder(holder)
        self.fit.stats.turretSlots.used = 1
        self.fit.stats.turretSlots.total = 0
        restrictionError = self.getRestrictionError(holder, Restriction.turretSlot)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.slotsMaxAllowed, 0)
        self.assertEqual(restrictionError.slotsUsed, 1)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailExcessSignleUndefinedOutput(self):
        # When stats module does not specify total slot amount,
        # make sure it's assumed to be 0
        item = self.ch.type_(typeId=1)
        item.slots = {Slot.turret}
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        self.fit.stats.turretSlots.used = 1
        self.fit.stats.turretSlots.total = None
        restrictionError = self.getRestrictionError(holder, Restriction.turretSlot)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.slotsMaxAllowed, 0)
        self.assertEqual(restrictionError.slotsUsed, 1)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailExcessMultiple(self):
        # Check that error works for multiple holders
        item = self.ch.type_(typeId=1)
        item.slots = {Slot.turret}
        holder1 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        holder2 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder1)
        self.trackHolder(holder2)
        self.fit.stats.turretSlots.used = 2
        self.fit.stats.turretSlots.total = 1
        restrictionError1 = self.getRestrictionError(holder1, Restriction.turretSlot)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.slotsMaxAllowed, 1)
        self.assertEqual(restrictionError1.slotsUsed, 2)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.turretSlot)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.slotsMaxAllowed, 1)
        self.assertEqual(restrictionError2.slotsUsed, 2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassEqual(self):
        item = self.ch.type_(typeId=1)
        item.slots = {Slot.turret}
        holder1 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        holder2 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder1)
        self.trackHolder(holder2)
        self.fit.stats.turretSlots.used = 2
        self.fit.stats.turretSlots.total = 2
        restrictionError1 = self.getRestrictionError(holder1, Restriction.turretSlot)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.turretSlot)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassGreater(self):
        item = self.ch.type_(typeId=1)
        item.slots = {Slot.turret}
        holder1 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        holder2 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder1)
        self.trackHolder(holder2)
        self.fit.stats.turretSlots.used = 2
        self.fit.stats.turretSlots.total = 5
        restrictionError1 = self.getRestrictionError(holder1, Restriction.turretSlot)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.turretSlot)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassOtherSlot(self):
        item = self.ch.type_(typeId=1)
        item.slots = {Slot.launcher}
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        self.fit.stats.turretSlots.used = 1
        self.fit.stats.turretSlots.total = 0
        restrictionError = self.getRestrictionError(holder, Restriction.turretSlot)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()
