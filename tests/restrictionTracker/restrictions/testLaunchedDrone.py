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
from eos.fit.holder.item import Drone, Character, Implant
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestLaunchedDrone(RestrictionTestCase):
    """Check functionality of max launched drone restriction"""

    def testFailExcessNoChar(self):
        # Check that any positive number of drones
        # results in error when no character is assigned
        # to fit
        item = self.ch.type_(typeId=1)
        holder = Mock(state=State.online, item=item, _location=Location.space, spec_set=Drone)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.launchedDrone)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.maxLaunchedDrones, 0)
        self.assertEqual(restrictionError.launchedDrones, 1)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailNoAttr(self):
        # Check that any positive number of drones
        # results in error when character is assigned
        # to fit, but no restriction attribute available
        item = self.ch.type_(typeId=1)
        holder1 = Mock(state=State.online, item=item, _location=Location.space, spec_set=Drone)
        self.trackHolder(holder1)
        holder2 = Mock(state=State.online, item=item, _location=Location.space, spec_set=Drone)
        self.trackHolder(holder2)
        charItem = self.ch.type_(typeId=2)
        charHolder = Mock(state=State.offline, item=charItem, _location=None, spec_set=Character)
        charHolder.attributes = {Attribute.maxActiveDrones: 1}
        self.setCharacter(charHolder)
        restrictionError1 = self.getRestrictionError(holder1, Restriction.launchedDrone)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.maxLaunchedDrones, 1)
        self.assertEqual(restrictionError1.launchedDrones, 2)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.launchedDrone)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.maxLaunchedDrones, 1)
        self.assertEqual(restrictionError2.launchedDrones, 2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailExcess(self):
        # Check that excessive number of drones results
        # in failure, even when character is assigned to
        # fit and max number attribute is available
        item = self.ch.type_(typeId=1)
        holder1 = Mock(state=State.online, item=item, _location=Location.space, spec_set=Drone)
        self.trackHolder(holder1)
        holder2 = Mock(state=State.online, item=item, _location=Location.space, spec_set=Drone)
        self.trackHolder(holder2)
        charItem = self.ch.type_(typeId=2)
        charHolder = Mock(state=State.offline, item=charItem, _location=None, spec_set=Character)
        charHolder.attributes = {Attribute.maxActiveDrones: 1}
        self.setCharacter(charHolder)
        restrictionError1 = self.getRestrictionError(holder1, Restriction.launchedDrone)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.maxLaunchedDrones, 1)
        self.assertEqual(restrictionError1.launchedDrones, 2)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.launchedDrone)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.maxLaunchedDrones, 1)
        self.assertEqual(restrictionError2.launchedDrones, 2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailExcessModified(self):
        # Check that modified attribute value is taken, not original
        item = self.ch.type_(typeId=1)
        holder1 = Mock(state=State.online, item=item, _location=Location.space, spec_set=Drone)
        self.trackHolder(holder1)
        holder2 = Mock(state=State.online, item=item, _location=Location.space, spec_set=Drone)
        self.trackHolder(holder2)
        charItem = self.ch.type_(typeId=2, attributes={Attribute.maxActiveDrones: 3})
        charHolder = Mock(state=State.offline, item=charItem, _location=None, spec_set=Character)
        charHolder.attributes = {Attribute.maxActiveDrones: 1}
        self.setCharacter(charHolder)
        restrictionError1 = self.getRestrictionError(holder1, Restriction.launchedDrone)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.maxLaunchedDrones, 1)
        self.assertEqual(restrictionError1.launchedDrones, 2)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.launchedDrone)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.maxLaunchedDrones, 1)
        self.assertEqual(restrictionError2.launchedDrones, 2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPass(self):
        # Check non-excessive number of drones
        item = self.ch.type_(typeId=1)
        holder1 = Mock(state=State.online, item=item, _location=Location.space, spec_set=Drone)
        self.trackHolder(holder1)
        holder2 = Mock(state=State.online, item=item, _location=Location.space, spec_set=Drone)
        self.trackHolder(holder2)
        charItem = self.ch.type_(typeId=2)
        charHolder = Mock(state=State.offline, item=charItem, _location=None, spec_set=Character)
        charHolder.attributes = {Attribute.maxActiveDrones: 5}
        self.setCharacter(charHolder)
        restrictionError1 = self.getRestrictionError(holder1, Restriction.launchedDrone)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.launchedDrone)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassState(self):
        # Check excessive number of drones, which are
        # not 'launched'
        item = self.ch.type_(typeId=1)
        holder1 = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        self.trackHolder(holder1)
        holder2 = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        self.trackHolder(holder2)
        charItem = self.ch.type_(typeId=2)
        charHolder = Mock(state=State.offline, item=charItem, _location=None, spec_set=Character)
        charHolder.attributes = {Attribute.maxActiveDrones: 1}
        self.setCharacter(charHolder)
        restrictionError1 = self.getRestrictionError(holder1, Restriction.launchedDrone)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.launchedDrone)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassNonDrone(self):
        # Check excessive number of non-drone items
        item = self.ch.type_(typeId=1)
        holder1 = Mock(state=State.offline, item=item, _location=Location.character, spec_set=Implant)
        holder1.state = State.online
        self.trackHolder(holder1)
        holder2 = Mock(state=State.offline, item=item, _location=Location.character, spec_set=Implant)
        holder2.state = State.online
        self.trackHolder(holder2)
        charItem = self.ch.type_(typeId=2)
        charHolder = Mock(state=State.offline, item=charItem, _location=None, spec_set=Character)
        charHolder.attributes = {Attribute.maxActiveDrones: 1}
        self.setCharacter(charHolder)
        restrictionError1 = self.getRestrictionError(holder1, Restriction.launchedDrone)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.launchedDrone)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()
