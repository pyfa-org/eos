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
from eos.fit.holder.item import Module, Ship
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestShipTypeGroup(RestrictionTestCase):
    """Check functionality of 'can fit to ship type/group' restriction"""

    def testFailType1(self):
        # Check that first type-restriction attribute affects
        # holder
        shipItem = self.ch.type_(typeId=772, groupId=31)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        item = self.ch.type_(typeId=1, attributes={Attribute.canFitShipType1: 10})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedTypes, (10,))
        self.assertCountEqual(restrictionError.allowedGroups, ())
        self.assertEqual(restrictionError.shipType, 772)
        self.assertEqual(restrictionError.shipGroup, 31)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailType2(self):
        # Check that second type-restriction attribute affects
        # holder
        shipItem = self.ch.type_(typeId=772, groupId=31)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        item = self.ch.type_(typeId=1, attributes={Attribute.canFitShipType2: 10})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedTypes, (10,))
        self.assertCountEqual(restrictionError.allowedGroups, ())
        self.assertEqual(restrictionError.shipType, 772)
        self.assertEqual(restrictionError.shipGroup, 31)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailType3(self):
        # Check that third type-restriction attribute affects
        # holder
        shipItem = self.ch.type_(typeId=772, groupId=31)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        item = self.ch.type_(typeId=1, attributes={Attribute.canFitShipType3: 10})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedTypes, (10,))
        self.assertCountEqual(restrictionError.allowedGroups, ())
        self.assertEqual(restrictionError.shipType, 772)
        self.assertEqual(restrictionError.shipGroup, 31)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailType4(self):
        # Check that fourth type-restriction attribute affects
        # holder
        shipItem = self.ch.type_(typeId=772, groupId=31)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        item = self.ch.type_(typeId=1, attributes={Attribute.canFitShipType4: 10})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedTypes, (10,))
        self.assertCountEqual(restrictionError.allowedGroups, ())
        self.assertEqual(restrictionError.shipType, 772)
        self.assertEqual(restrictionError.shipGroup, 31)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailType5(self):
        # Check that fifth type-restriction attribute affects
        # holder
        shipItem = self.ch.type_(typeId=772, groupId=31)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        item = self.ch.type_(typeId=1, attributes={Attribute.fitsToShipType: 10})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedTypes, (10,))
        self.assertCountEqual(restrictionError.allowedGroups, ())
        self.assertEqual(restrictionError.shipType, 772)
        self.assertEqual(restrictionError.shipGroup, 31)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailTypeMultipleDifferent(self):
        shipItem = self.ch.type_(typeId=772, groupId=31)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        item = self.ch.type_(typeId=1, attributes={Attribute.canFitShipType1: 10, Attribute.canFitShipType2: 11})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedTypes, (10, 11))
        self.assertCountEqual(restrictionError.allowedGroups, ())
        self.assertEqual(restrictionError.shipType, 772)
        self.assertEqual(restrictionError.shipGroup, 31)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailTypeMultipleSame(self):
        shipItem = self.ch.type_(typeId=772, groupId=31)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        item = self.ch.type_(typeId=1, attributes={Attribute.canFitShipType1: 10, Attribute.canFitShipType2: 10})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedTypes, (10,))
        self.assertCountEqual(restrictionError.allowedGroups, ())
        self.assertEqual(restrictionError.shipType, 772)
        self.assertEqual(restrictionError.shipGroup, 31)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailGroup1(self):
        # Check that first group-restriction attribute affects
        # holder
        shipItem = self.ch.type_(typeId=772, groupId=31)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        item = self.ch.type_(typeId=1, attributes={Attribute.canFitShipGroup1: 38})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedTypes, ())
        self.assertCountEqual(restrictionError.allowedGroups, (38,))
        self.assertEqual(restrictionError.shipType, 772)
        self.assertEqual(restrictionError.shipGroup, 31)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailGroup2(self):
        # Check that second group-restriction attribute affects
        # holder
        shipItem = self.ch.type_(typeId=772, groupId=31)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        item = self.ch.type_(typeId=1, attributes={Attribute.canFitShipGroup2: 38})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedTypes, ())
        self.assertCountEqual(restrictionError.allowedGroups, (38,))
        self.assertEqual(restrictionError.shipType, 772)
        self.assertEqual(restrictionError.shipGroup, 31)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailGroup3(self):
        # Check that third group-restriction attribute affects
        # holder
        shipItem = self.ch.type_(typeId=772, groupId=31)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        item = self.ch.type_(typeId=1, attributes={Attribute.canFitShipGroup3: 38})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedTypes, ())
        self.assertCountEqual(restrictionError.allowedGroups, (38,))
        self.assertEqual(restrictionError.shipType, 772)
        self.assertEqual(restrictionError.shipGroup, 31)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailGroup4(self):
        # Check that fourth group-restriction attribute affects
        # holder
        shipItem = self.ch.type_(typeId=772, groupId=31)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        item = self.ch.type_(typeId=1, attributes={Attribute.canFitShipGroup4: 38})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedTypes, ())
        self.assertCountEqual(restrictionError.allowedGroups, (38,))
        self.assertEqual(restrictionError.shipType, 772)
        self.assertEqual(restrictionError.shipGroup, 31)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailGroupMultipleDifferent(self):
        shipItem = self.ch.type_(typeId=772, groupId=31)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        item = self.ch.type_(typeId=1, attributes={Attribute.canFitShipGroup1: 38, Attribute.canFitShipGroup2: 83})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedTypes, ())
        self.assertCountEqual(restrictionError.allowedGroups, (38, 83))
        self.assertEqual(restrictionError.shipType, 772)
        self.assertEqual(restrictionError.shipGroup, 31)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailGroupMultipleSame(self):
        shipItem = self.ch.type_(typeId=772, groupId=31)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        item = self.ch.type_(typeId=1, attributes={Attribute.canFitShipGroup1: 38, Attribute.canFitShipGroup2: 38})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedTypes, ())
        self.assertCountEqual(restrictionError.allowedGroups, (38,))
        self.assertEqual(restrictionError.shipType, 772)
        self.assertEqual(restrictionError.shipGroup, 31)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailCombined(self):
        # Check that failure is appropriately generated when
        # holder specifies both type and group restrictions
        shipItem = self.ch.type_(typeId=772, groupId=31)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        item = self.ch.type_(typeId=1, attributes={Attribute.canFitShipType1: 1089, Attribute.canFitShipGroup1: 23})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedTypes, (1089,))
        self.assertCountEqual(restrictionError.allowedGroups, (23,))
        self.assertEqual(restrictionError.shipType, 772)
        self.assertEqual(restrictionError.shipGroup, 31)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailNoShip(self):
        # Absent ship should trigger this error too
        item = self.ch.type_(typeId=1, attributes={Attribute.canFitShipType1: 10})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedTypes, (10,))
        self.assertCountEqual(restrictionError.allowedGroups, ())
        self.assertEqual(restrictionError.shipType, None)
        self.assertEqual(restrictionError.shipGroup, None)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailAttrOriginal(self):
        # Make sure original value is taken
        shipItem = self.ch.type_(typeId=772, groupId=31)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        item = self.ch.type_(typeId=1, attributes={Attribute.canFitShipType1: 10})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        holder.attributes = {Attribute.canFitShipType1: 772}
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedTypes, (10,))
        self.assertCountEqual(restrictionError.allowedGroups, ())
        self.assertEqual(restrictionError.shipType, 772)
        self.assertEqual(restrictionError.shipGroup, 31)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassTypeMatch(self):
        # When type of ship matches type-restriction attribute,
        # no error should be raised
        shipItem = self.ch.type_(typeId=554, groupId=23)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        item = self.ch.type_(typeId=1, attributes={Attribute.canFitShipType1: 554})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassGroupMatch(self):
        # When type of ship matches group-restriction attribute,
        # no error should be raised
        shipItem = self.ch.type_(typeId=554, groupId=23)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        item = self.ch.type_(typeId=1, attributes={Attribute.canFitShipGroup1: 23})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassCombinedTypeMatch(self):
        # Check that it's enough to match type condition
        # to be fittable, even if both conditions are specified
        shipItem = self.ch.type_(typeId=671, groupId=31)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        item = self.ch.type_(typeId=1, attributes={Attribute.canFitShipType1: 671, Attribute.canFitShipGroup1: 38})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassCombinedGroupMatch(self):
        # Check that it's enough to match group condition
        # to be fittable, even if both conditions are specified
        shipItem = self.ch.type_(typeId=554, groupId=23)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        item = self.ch.type_(typeId=1, attributes={Attribute.canFitShipType1: 1089, Attribute.canFitShipGroup1: 23})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassNonShipHolder(self):
        # Holders not belonging to ship shouldn't be affected
        shipItem = self.ch.type_(typeId=772, groupId=31)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        item = self.ch.type_(typeId=1, attributes={Attribute.canFitShipType1: 10})
        holder = Mock(state=State.offline, item=item, _location=None, spec_set=Module)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()
