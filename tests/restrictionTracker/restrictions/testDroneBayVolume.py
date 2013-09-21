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


class TestDroneBayVolume(RestrictionTestCase):
    """Check functionality of drone bay volume restriction"""

    def testFailExcessNoShip(self):
        # Make sure error is raised on fits without ship
        item = self.ch.type_(typeId=1, attributes={Attribute.volume: 0})
        holder = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        holder.attributes = {Attribute.volume: 50}
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.droneBayVolume)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.output, 0)
        self.assertEqual(restrictionError.totalUsage, 50)
        self.assertEqual(restrictionError.holderConsumption, 50)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailExcessShipNoAttr(self):
        # When ship is assigned, but doesn't have calibration output
        # attribute, error should be raised for calibration consumers too
        item = self.ch.type_(typeId=1, attributes={Attribute.volume: 0})
        holder = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        holder.attributes = {Attribute.volume: 50}
        self.trackHolder(holder)
        shipItem = self.ch.type_(typeId=2)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {}
        self.setShip(shipHolder)
        restrictionError = self.getRestrictionError(holder, Restriction.droneBayVolume)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.output, 0)
        self.assertEqual(restrictionError.totalUsage, 50)
        self.assertEqual(restrictionError.holderConsumption, 50)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailExcessSingle(self):
        # When ship provides calibration output, but single consumer
        # demands for more, error should be raised
        item = self.ch.type_(typeId=1, attributes={Attribute.volume: 0})
        holder = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        holder.attributes = {Attribute.volume: 50}
        self.trackHolder(holder)
        shipItem = self.ch.type_(typeId=2)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {Attribute.droneCapacity: 40}
        self.setShip(shipHolder)
        restrictionError = self.getRestrictionError(holder, Restriction.droneBayVolume)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.output, 40)
        self.assertEqual(restrictionError.totalUsage, 50)
        self.assertEqual(restrictionError.holderConsumption, 50)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailExcessMultiple(self):
        # When multiple consumers require less than calibration output
        # alone, but in sum want more than total output, it should
        # be erroneous situation
        item = self.ch.type_(typeId=1, attributes={Attribute.volume: 0})
        holder1 = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        holder1.attributes = {Attribute.volume: 25}
        self.trackHolder(holder1)
        holder2 = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        holder2.attributes = {Attribute.volume: 20}
        self.trackHolder(holder2)
        shipItem = self.ch.type_(typeId=2)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {Attribute.droneCapacity: 40}
        self.setShip(shipHolder)
        restrictionError1 = self.getRestrictionError(holder1, Restriction.droneBayVolume)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.output, 40)
        self.assertEqual(restrictionError1.totalUsage, 45)
        self.assertEqual(restrictionError1.holderConsumption, 25)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.droneBayVolume)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.output, 40)
        self.assertEqual(restrictionError2.totalUsage, 45)
        self.assertEqual(restrictionError2.holderConsumption, 20)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailExcessModified(self):
        # Make sure modified calibration values are taken
        item = self.ch.type_(typeId=1, attributes={Attribute.volume: 40})
        holder = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        holder.attributes = {Attribute.volume: 100}
        self.trackHolder(holder)
        shipItem = self.ch.type_(typeId=2, attributes={Attribute.droneCapacity: 45})
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {Attribute.droneCapacity: 50}
        self.setShip(shipHolder)
        restrictionError = self.getRestrictionError(holder, Restriction.droneBayVolume)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.output, 50)
        self.assertEqual(restrictionError.totalUsage, 100)
        self.assertEqual(restrictionError.holderConsumption, 100)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testMixUsageNegative(self):
        # If some holder has negative usage and calibration error is
        # still raised, check it's not raised for holder with
        # negative usage
        item = self.ch.type_(typeId=1, attributes={Attribute.volume: 0})
        holder1 = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        holder1.attributes = {Attribute.volume: 100}
        self.trackHolder(holder1)
        holder2 = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        holder2.attributes = {Attribute.volume: -10}
        self.trackHolder(holder2)
        shipItem = self.ch.type_(typeId=2)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {Attribute.droneCapacity: 50}
        self.setShip(shipHolder)
        restrictionError1 = self.getRestrictionError(holder1, Restriction.droneBayVolume)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.output, 50)
        self.assertEqual(restrictionError1.totalUsage, 90)
        self.assertEqual(restrictionError1.holderConsumption, 100)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.droneBayVolume)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testMixUsageZero(self):
        # If some holder has zero usage and calibration error is
        # still raised, check it's not raised for holder with
        # zero usage
        item = self.ch.type_(typeId=1, attributes={Attribute.volume: 0})
        holder1 = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        holder1.attributes = {Attribute.volume: 100}
        self.trackHolder(holder1)
        holder2 = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        holder2.attributes = {Attribute.volume: 0}
        self.trackHolder(holder2)
        shipItem = self.ch.type_(typeId=2)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {Attribute.droneCapacity: 50}
        self.setShip(shipHolder)
        restrictionError1 = self.getRestrictionError(holder1, Restriction.droneBayVolume)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.output, 50)
        self.assertEqual(restrictionError1.totalUsage, 100)
        self.assertEqual(restrictionError1.holderConsumption, 100)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.droneBayVolume)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPass(self):
        # When total consumption is less than output,
        # no errors should be raised
        item = self.ch.type_(typeId=1, attributes={Attribute.volume: 0})
        holder1 = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        holder1.attributes = {Attribute.volume: 25}
        self.trackHolder(holder1)
        holder2 = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        holder2.attributes = {Attribute.volume: 20}
        self.trackHolder(holder2)
        shipItem = self.ch.type_(typeId=2)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {Attribute.droneCapacity: 50}
        self.setShip(shipHolder)
        restrictionError1 = self.getRestrictionError(holder1, Restriction.droneBayVolume)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.droneBayVolume)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassNoOriginalAttr(self):
        # When added holder's item doesn't have original attribute,
        # holder shouldn't be tracked by register, and thus, no
        # errors should be raised
        item = self.ch.type_(typeId=1)
        holder = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        holder.attributes = {Attribute.volume: 100}
        self.trackHolder(holder)
        shipItem = self.ch.type_(typeId=2)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {Attribute.droneCapacity: 50}
        self.setShip(shipHolder)
        restrictionError = self.getRestrictionError(holder, Restriction.droneBayVolume)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassNegativeConsumption(self):
        # Check that even if use of one holder exceeds
        # calibration output, negative use of other holder may help
        # to avoid raising error
        item = self.ch.type_(typeId=1, attributes={Attribute.volume: 0})
        holder1 = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        holder1.attributes = {Attribute.volume: 50}
        self.trackHolder(holder1)
        holder2 = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        holder2.attributes = {Attribute.volume: -15}
        self.trackHolder(holder2)
        shipItem = self.ch.type_(typeId=2)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {Attribute.droneCapacity: 40}
        self.setShip(shipHolder)
        restrictionError1 = self.getRestrictionError(holder1, Restriction.droneBayVolume)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.droneBayVolume)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassOtherClass(self):
        # Make sure holders of all classes are affected
        item = self.ch.type_(typeId=1, attributes={Attribute.volume: 0})
        holder = Mock(state=State.offline, item=item, _location=Location.character, spec_set=Implant)
        holder.attributes = {Attribute.volume: 50}
        self.trackHolder(holder)
        shipItem = self.ch.type_(typeId=2)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {Attribute.droneCapacity: 40}
        self.setShip(shipHolder)
        restrictionError = self.getRestrictionError(holder, Restriction.droneBayVolume)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()
