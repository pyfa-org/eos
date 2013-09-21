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

from eos.const.eos import Restriction, Location, State
from eos.const.eve import Attribute
from eos.fit.holder.item import Module
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestMaxGroupActive(RestrictionTestCase):
    """Check functionality of max group active restriction"""

    def testFailExcessAll(self):
        # Make sure error is raised for all holders exceeding
        # their group restriction
        item = self.ch.type_(typeId=1, groupId=6, attributes={Attribute.maxGroupActive: 1})
        holder1 = Mock(state=State.active, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder1)
        holder2 = Mock(state=State.active, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder2)
        restrictionError1 = self.getRestrictionError(holder1, Restriction.maxGroupActive)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.maxGroup, 1)
        self.assertEqual(restrictionError1.holderGroup, 6)
        self.assertEqual(restrictionError1.groupHolders, 2)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.maxGroupActive)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.maxGroup, 1)
        self.assertEqual(restrictionError2.holderGroup, 6)
        self.assertEqual(restrictionError2.groupHolders, 2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testMixExcessOne(self):
        # Make sure error is raised for just holders which excess
        # restriction, even if both are from the same group
        item1 = self.ch.type_(typeId=1, groupId=92, attributes={Attribute.maxGroupActive: 1})
        holder1 = Mock(state=State.active, item=item1, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder1)
        item2 = self.ch.type_(typeId=2, groupId=92, attributes={Attribute.maxGroupActive: 2})
        holder2 = Mock(state=State.active, item=item2, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder2)
        restrictionError1 = self.getRestrictionError(holder1, Restriction.maxGroupActive)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.maxGroup, 1)
        self.assertEqual(restrictionError1.holderGroup, 92)
        self.assertEqual(restrictionError1.groupHolders, 2)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.maxGroupActive)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testMixExcessOriginal(self):
        # Check that original item attributes are used
        item1 = self.ch.type_(typeId=1, groupId=61, attributes={Attribute.maxGroupActive: 1})
        holder1 = Mock(state=State.active, item=item1, _location=Location.ship, spec_set=Module)
        holder1.attributes = {Attribute.maxGroupActive: 2}
        self.trackHolder(holder1)
        item2 = self.ch.type_(typeId=2, groupId=61, attributes={Attribute.maxGroupActive: 2})
        holder2 = Mock(state=State.active, item=item2, _location=Location.ship, spec_set=Module)
        holder2.attributes = {Attribute.maxGroupActive: 1}
        self.trackHolder(holder2)
        restrictionError1 = self.getRestrictionError(holder1, Restriction.maxGroupActive)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.maxGroup, 1)
        self.assertEqual(restrictionError1.holderGroup, 61)
        self.assertEqual(restrictionError1.groupHolders, 2)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.maxGroupActive)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPass(self):
        # Make sure no errors are raised when number of added
        # items doesn't exceed any restrictions
        item = self.ch.type_(typeId=1, groupId=860, attributes={Attribute.maxGroupActive: 2})
        holder1 = Mock(state=State.active, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder1)
        holder2 = Mock(state=State.active, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder2)
        restrictionError1 = self.getRestrictionError(holder1, Restriction.maxGroupActive)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.maxGroupActive)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassHolderNoneGroup(self):
        # Check that holders with None group are not affected
        item = self.ch.type_(typeId=1, groupId=None, attributes={Attribute.maxGroupActive: 1})
        holder1 = Mock(state=State.active, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder1)
        holder2 = Mock(state=State.active, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder2)
        restrictionError1 = self.getRestrictionError(holder1, Restriction.maxGroupActive)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.maxGroupActive)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassState(self):
        # No errors should occur if holders are not active+
        item = self.ch.type_(typeId=1, groupId=886, attributes={Attribute.maxGroupActive: 1})
        holder1 = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder1)
        holder2 = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder2)
        restrictionError1 = self.getRestrictionError(holder1, Restriction.maxGroupActive)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.maxGroupActive)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassHolderNonShip(self):
        # Holders not belonging to ship shouldn't be affected
        item = self.ch.type_(typeId=1, groupId=12, attributes={Attribute.maxGroupActive: 1})
        holder1 = Mock(state=State.active, item=item, _location=None, spec_set=Module)
        self.trackHolder(holder1)
        holder2 = Mock(state=State.active, item=item, _location=None, spec_set=Module)
        self.trackHolder(holder2)
        restrictionError1 = self.getRestrictionError(holder1, Restriction.maxGroupActive)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.maxGroupActive)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()
