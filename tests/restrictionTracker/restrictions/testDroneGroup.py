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
from eos.const.eve import Attribute
from eos.fit.holder.item import Drone, Ship, Implant
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestDroneGroup(RestrictionTestCase):
    """Check functionality of drone group restriction"""

    def testFailMismatch1(self):
        # Check that error is returned on attempt
        # to add drone from group mismatching to
        # first restriction attribute
        item = self.ch.type_(typeId=1, groupId=56)
        holder = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        self.trackHolder(holder)
        shipItem = self.ch.type_(typeId=2, attributes={Attribute.allowedDroneGroup1: 4})
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        restrictionError = self.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedGroups, (4,))
        self.assertEqual(restrictionError.holderGroup, 56)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailMismatch2(self):
        # Check that error is returned on attempt
        # to add drone from group mismatching to
        # second restriction attribute
        item = self.ch.type_(typeId=1, groupId=797)
        holder = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        self.trackHolder(holder)
        shipItem = self.ch.type_(typeId=2, attributes={Attribute.allowedDroneGroup2: 69})
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        restrictionError = self.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedGroups, (69,))
        self.assertEqual(restrictionError.holderGroup, 797)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailMismatchCombined(self):
        # Check that error is returned on attempt
        # to add drone from group mismatching to
        # both restriction attributes
        item = self.ch.type_(typeId=1, groupId=803)
        holder = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        self.trackHolder(holder)
        shipItem = self.ch.type_(typeId=2, attributes={Attribute.allowedDroneGroup1: 48, Attribute.allowedDroneGroup2: 106})
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        restrictionError = self.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedGroups, (48, 106))
        self.assertEqual(restrictionError.holderGroup, 803)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailMismatchOriginal(self):
        # Check that error is returned on attempt
        # to add drone from group mismatching to
        # original restriction attribute, but matching
        # to modified restriction attribute. Effectively
        # we check that original attribute value is taken
        item = self.ch.type_(typeId=1, groupId=37)
        holder = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        self.trackHolder(holder)
        shipItem = self.ch.type_(typeId=2, attributes={Attribute.allowedDroneGroup1: 59})
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {Attribute.allowedDroneGroup1: 37}
        self.setShip(shipHolder)
        restrictionError = self.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedGroups, (59,))
        self.assertEqual(restrictionError.holderGroup, 37)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailDroneNone(self):
        # Check that drone from None group is subject
        # to restriction
        item = self.ch.type_(typeId=1, groupId=None)
        holder = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        self.trackHolder(holder)
        shipItem = self.ch.type_(typeId=2, attributes={Attribute.allowedDroneGroup1: 1896})
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        restrictionError = self.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedGroups, (1896,))
        self.assertEqual(restrictionError.holderGroup, None)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassNoShip(self):
        # Check that restriction isn't applied
        # when fit doesn't have ship
        item = self.ch.type_(typeId=1, groupId=None)
        holder = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassShipNoRestriction(self):
        # Check that restriction isn't applied
        # when fit has ship, but without restriction
        # attribute
        item = self.ch.type_(typeId=1, groupId=71)
        holder = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        self.trackHolder(holder)
        shipItem = self.ch.type_(typeId=2)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        restrictionError = self.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassNonDrone(self):
        # Check that restriction is not applied
        # to holders which are not drones
        item = self.ch.type_(typeId=1, groupId=56)
        holder = Mock(state=State.offline, item=item, _location=Location.character, spec_set=Implant)
        self.trackHolder(holder)
        shipItem = self.ch.type_(typeId=2, attributes={Attribute.allowedDroneGroup1: 4})
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        restrictionError = self.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassMatch1(self):
        # Check that no error raised when drone of group
        # matching to first restriction attribute is added
        item = self.ch.type_(typeId=1, groupId=22)
        holder = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        self.trackHolder(holder)
        shipItem = self.ch.type_(typeId=2, attributes={Attribute.allowedDroneGroup1: 22})
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        restrictionError = self.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassMatch2(self):
        # Check that no error raised when drone of group
        # matching to second restriction attribute is added
        item = self.ch.type_(typeId=1, groupId=67)
        holder = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        self.trackHolder(holder)
        shipItem = self.ch.type_(typeId=2, attributes={Attribute.allowedDroneGroup2: 67})
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        restrictionError = self.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassMatchCombination(self):
        # Check that no error raised when drone of group
        # matching to any of two restriction attributes
        # is added
        item = self.ch.type_(typeId=1, groupId=53)
        holder = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        self.trackHolder(holder)
        shipItem = self.ch.type_(typeId=2, attributes={Attribute.allowedDroneGroup1: 907, Attribute.allowedDroneGroup2: 53})
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        restrictionError = self.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()
