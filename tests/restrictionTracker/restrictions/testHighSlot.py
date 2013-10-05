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

from eos.const.eos import Location, Restriction, State
from eos.fit.holder.item import Implant, Module
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestHighSlot(RestrictionTestCase):
    """Check functionality of high slot amount restriction"""

    def testFailExcessSignle(self):
        # Check that error is raised when number of used
        # slots exceeds slot amount provided by ship
        item = self.ch.type_(typeId=1)
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.fit.modules.high.append(holder)
        self.fit.stats.highSlots.used = 1
        self.fit.stats.highSlots.total = 0
        restrictionError = self.getRestrictionError(holder, Restriction.highSlot)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.slotsMaxAllowed, 0)
        self.assertEqual(restrictionError.slotsUsed, 1)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailExcessSignleOtherClassLocation(self):
        # Make sure holders of all classes are affected
        item = self.ch.type_(typeId=1)
        holder = Mock(state=State.offline, item=item, _location=Location.character, spec_set=Implant)
        self.fit.modules.high.append(holder)
        self.fit.stats.highSlots.used = 1
        self.fit.stats.highSlots.total = 0
        restrictionError = self.getRestrictionError(holder, Restriction.highSlot)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.slotsMaxAllowed, 0)
        self.assertEqual(restrictionError.slotsUsed, 1)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailExcessSignleUndefinedOutput(self):
        # When stats module does not specify total slot amount,
        # make sure it's assumed to be 0
        item = self.ch.type_(typeId=1)
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.fit.modules.high.append(holder)
        self.fit.stats.highSlots.used = 1
        self.fit.stats.highSlots.total = None
        restrictionError = self.getRestrictionError(holder, Restriction.highSlot)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.slotsMaxAllowed, 0)
        self.assertEqual(restrictionError.slotsUsed, 1)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailExcessMultiple(self):
        # Check that error works for multiple holders, and raised
        # only for those which lie out of bounds
        item = self.ch.type_(typeId=1)
        holder1 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        holder2 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.fit.modules.high.append(holder1)
        self.fit.modules.high.append(holder2)
        self.fit.stats.highSlots.used = 2
        self.fit.stats.highSlots.total = 1
        restrictionError1 = self.getRestrictionError(holder1, Restriction.highSlot)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.highSlot)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.slotsMaxAllowed, 1)
        self.assertEqual(restrictionError2.slotsUsed, 2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailExcessMultipleWithNones(self):
        # Make sure Nones are processed properly
        item = self.ch.type_(typeId=1)
        holder1 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        holder2 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        holder3 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.fit.modules.high.append(None)
        self.fit.modules.high.append(holder1)
        self.fit.modules.high.append(None)
        self.fit.modules.high.append(None)
        self.fit.modules.high.append(holder2)
        self.fit.modules.high.append(None)
        self.fit.modules.high.append(holder3)
        self.fit.stats.highSlots.used = 7
        self.fit.stats.highSlots.total = 3
        restrictionError1 = self.getRestrictionError(holder1, Restriction.highSlot)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.highSlot)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.slotsMaxAllowed, 3)
        self.assertEqual(restrictionError2.slotsUsed, 7)
        restrictionError3 = self.getRestrictionError(holder2, Restriction.highSlot)
        self.assertIsNotNone(restrictionError3)
        self.assertEqual(restrictionError3.slotsMaxAllowed, 3)
        self.assertEqual(restrictionError3.slotsUsed, 7)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassEqual(self):
        item = self.ch.type_(typeId=1)
        holder1 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        holder2 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.fit.modules.high.append(holder1)
        self.fit.modules.high.append(holder2)
        self.fit.stats.highSlots.used = 2
        self.fit.stats.highSlots.total = 2
        restrictionError1 = self.getRestrictionError(holder1, Restriction.highSlot)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.highSlot)
        self.assertIsNone(restrictionError2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassGreater(self):
        item = self.ch.type_(typeId=1)
        holder1 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        holder2 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.fit.modules.high.append(holder1)
        self.fit.modules.high.append(holder2)
        self.fit.stats.highSlots.used = 2
        self.fit.stats.highSlots.total = 5
        restrictionError1 = self.getRestrictionError(holder1, Restriction.highSlot)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.highSlot)
        self.assertIsNone(restrictionError2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassOtherContainer(self):
        item = self.ch.type_(typeId=1)
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.fit.modules.med.append(holder)
        self.fit.stats.highSlots.used = 1
        self.fit.stats.highSlots.total = 0
        restrictionError = self.getRestrictionError(holder, Restriction.highSlot)
        self.assertIsNone(restrictionError)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()
