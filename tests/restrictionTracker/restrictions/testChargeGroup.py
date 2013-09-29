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
from eos.fit.holder.item import Module, Charge
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestChargeGroup(RestrictionTestCase):
    """Check functionality of charge group restriction"""

    def testFailGroup1(self):
        chargeItem = self.ch.type_(typeId=1, groupId=1008)
        chargeHolder = Mock(state=State.offline, item=chargeItem, _location=None, spec_set=Charge)
        containerItem = self.ch.type_(typeId=2, attributes={Attribute.chargeGroup1: 3})
        containerHolder = Mock(state=State.offline, item=containerItem, _location=Location.ship, spec_set=Module)
        containerHolder.charge = chargeHolder
        chargeHolder.container = containerHolder
        self.trackHolder(containerHolder)
        self.trackHolder(chargeHolder)
        restrictionError1 = self.getRestrictionError(containerHolder, Restriction.chargeGroup)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(chargeHolder, Restriction.chargeGroup)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(len(restrictionError2.allowedGroups), 1)
        self.assertIn(3, restrictionError2.allowedGroups)
        self.assertEqual(restrictionError2.holderGroup, 1008)
        self.untrackHolder(containerHolder)
        self.untrackHolder(chargeHolder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailGroup2(self):
        chargeItem = self.ch.type_(typeId=1, groupId=1008)
        chargeHolder = Mock(state=State.offline, item=chargeItem, _location=None, spec_set=Charge)
        containerItem = self.ch.type_(typeId=2, attributes={Attribute.chargeGroup2: 3})
        containerHolder = Mock(state=State.offline, item=containerItem, _location=Location.ship, spec_set=Module)
        containerHolder.charge = chargeHolder
        chargeHolder.container = containerHolder
        self.trackHolder(containerHolder)
        self.trackHolder(chargeHolder)
        restrictionError1 = self.getRestrictionError(containerHolder, Restriction.chargeGroup)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(chargeHolder, Restriction.chargeGroup)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(len(restrictionError2.allowedGroups), 1)
        self.assertIn(3, restrictionError2.allowedGroups)
        self.assertEqual(restrictionError2.holderGroup, 1008)
        self.untrackHolder(containerHolder)
        self.untrackHolder(chargeHolder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailGroup3(self):
        chargeItem = self.ch.type_(typeId=1, groupId=1008)
        chargeHolder = Mock(state=State.offline, item=chargeItem, _location=None, spec_set=Charge)
        containerItem = self.ch.type_(typeId=2, attributes={Attribute.chargeGroup3: 3})
        containerHolder = Mock(state=State.offline, item=containerItem, _location=Location.ship, spec_set=Module)
        containerHolder.charge = chargeHolder
        chargeHolder.container = containerHolder
        self.trackHolder(containerHolder)
        self.trackHolder(chargeHolder)
        restrictionError1 = self.getRestrictionError(containerHolder, Restriction.chargeGroup)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(chargeHolder, Restriction.chargeGroup)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(len(restrictionError2.allowedGroups), 1)
        self.assertIn(3, restrictionError2.allowedGroups)
        self.assertEqual(restrictionError2.holderGroup, 1008)
        self.untrackHolder(containerHolder)
        self.untrackHolder(chargeHolder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailGroup4(self):
        chargeItem = self.ch.type_(typeId=1, groupId=1008)
        chargeHolder = Mock(state=State.offline, item=chargeItem, _location=None, spec_set=Charge)
        containerItem = self.ch.type_(typeId=2, attributes={Attribute.chargeGroup4: 3})
        containerHolder = Mock(state=State.offline, item=containerItem, _location=Location.ship, spec_set=Module)
        containerHolder.charge = chargeHolder
        chargeHolder.container = containerHolder
        self.trackHolder(containerHolder)
        self.trackHolder(chargeHolder)
        restrictionError1 = self.getRestrictionError(containerHolder, Restriction.chargeGroup)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(chargeHolder, Restriction.chargeGroup)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(len(restrictionError2.allowedGroups), 1)
        self.assertIn(3, restrictionError2.allowedGroups)
        self.assertEqual(restrictionError2.holderGroup, 1008)
        self.untrackHolder(containerHolder)
        self.untrackHolder(chargeHolder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailGroup5(self):
        chargeItem = self.ch.type_(typeId=1, groupId=1008)
        chargeHolder = Mock(state=State.offline, item=chargeItem, _location=None, spec_set=Charge)
        containerItem = self.ch.type_(typeId=2, attributes={Attribute.chargeGroup5: 3})
        containerHolder = Mock(state=State.offline, item=containerItem, _location=Location.ship, spec_set=Module)
        containerHolder.charge = chargeHolder
        chargeHolder.container = containerHolder
        self.trackHolder(containerHolder)
        self.trackHolder(chargeHolder)
        restrictionError1 = self.getRestrictionError(containerHolder, Restriction.chargeGroup)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(chargeHolder, Restriction.chargeGroup)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(len(restrictionError2.allowedGroups), 1)
        self.assertIn(3, restrictionError2.allowedGroups)
        self.assertEqual(restrictionError2.holderGroup, 1008)
        self.untrackHolder(containerHolder)
        self.untrackHolder(chargeHolder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailChargeNone(self):
        chargeItem = self.ch.type_(typeId=1, groupId=None)
        chargeHolder = Mock(state=State.offline, item=chargeItem, _location=None, spec_set=Charge)
        containerItem = self.ch.type_(typeId=2, attributes={Attribute.chargeGroup1: 3})
        containerHolder = Mock(state=State.offline, item=containerItem, _location=Location.ship, spec_set=Module)
        containerHolder.charge = chargeHolder
        chargeHolder.container = containerHolder
        self.trackHolder(containerHolder)
        self.trackHolder(chargeHolder)
        restrictionError1 = self.getRestrictionError(containerHolder, Restriction.chargeGroup)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(chargeHolder, Restriction.chargeGroup)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(len(restrictionError2.allowedGroups), 1)
        self.assertIn(3, restrictionError2.allowedGroups)
        self.assertEqual(restrictionError2.holderGroup, None)
        self.untrackHolder(containerHolder)
        self.untrackHolder(chargeHolder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailMultipleSame(self):
        chargeItem = self.ch.type_(typeId=1, groupId=1008)
        chargeHolder = Mock(state=State.offline, item=chargeItem, _location=None, spec_set=Charge)
        containerItem = self.ch.type_(typeId=2, attributes={Attribute.chargeGroup3: 3, Attribute.chargeGroup5: 3})
        containerHolder = Mock(state=State.offline, item=containerItem, _location=Location.ship, spec_set=Module)
        containerHolder.charge = chargeHolder
        chargeHolder.container = containerHolder
        self.trackHolder(containerHolder)
        self.trackHolder(chargeHolder)
        restrictionError1 = self.getRestrictionError(containerHolder, Restriction.chargeGroup)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(chargeHolder, Restriction.chargeGroup)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(len(restrictionError2.allowedGroups), 1)
        self.assertIn(3, restrictionError2.allowedGroups)
        self.assertEqual(restrictionError2.holderGroup, 1008)
        self.untrackHolder(containerHolder)
        self.untrackHolder(chargeHolder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailMultipleDifferent(self):
        chargeItem = self.ch.type_(typeId=1, groupId=1008)
        chargeHolder = Mock(state=State.offline, item=chargeItem, _location=None, spec_set=Charge)
        containerItem = self.ch.type_(typeId=2, attributes={Attribute.chargeGroup3: 5, Attribute.chargeGroup5: 3})
        containerHolder = Mock(state=State.offline, item=containerItem, _location=Location.ship, spec_set=Module)
        containerHolder.charge = chargeHolder
        chargeHolder.container = containerHolder
        self.trackHolder(containerHolder)
        self.trackHolder(chargeHolder)
        restrictionError1 = self.getRestrictionError(containerHolder, Restriction.chargeGroup)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(chargeHolder, Restriction.chargeGroup)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(len(restrictionError2.allowedGroups), 2)
        self.assertIn(3, restrictionError2.allowedGroups)
        self.assertIn(5, restrictionError2.allowedGroups)
        self.assertEqual(restrictionError2.holderGroup, 1008)
        self.untrackHolder(containerHolder)
        self.untrackHolder(chargeHolder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailoriginalAttr(self):
        chargeItem = self.ch.type_(typeId=1, groupId=1008)
        chargeHolder = Mock(state=State.offline, item=chargeItem, _location=None, spec_set=Charge)
        containerItem = self.ch.type_(typeId=2, attributes={Attribute.chargeGroup1: 3})
        containerHolder = Mock(state=State.offline, item=containerItem, _location=Location.ship, spec_set=Module)
        containerHolder.attributes = {Attribute.chargeGroup1: 1008}
        containerHolder.charge = chargeHolder
        chargeHolder.container = containerHolder
        self.trackHolder(containerHolder)
        self.trackHolder(chargeHolder)
        restrictionError1 = self.getRestrictionError(containerHolder, Restriction.chargeGroup)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(chargeHolder, Restriction.chargeGroup)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(len(restrictionError2.allowedGroups), 1)
        self.assertIn(3, restrictionError2.allowedGroups)
        self.assertEqual(restrictionError2.holderGroup, 1008)
        self.untrackHolder(containerHolder)
        self.untrackHolder(chargeHolder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassMatch(self):
        chargeItem = self.ch.type_(typeId=1, groupId=3)
        chargeHolder = Mock(state=State.offline, item=chargeItem, _location=None, spec_set=Charge)
        containerItem = self.ch.type_(typeId=2, attributes={Attribute.chargeGroup1: 3})
        containerHolder = Mock(state=State.offline, item=containerItem, _location=Location.ship, spec_set=Module)
        containerHolder.charge = chargeHolder
        chargeHolder.container = containerHolder
        self.trackHolder(containerHolder)
        self.trackHolder(chargeHolder)
        restrictionError1 = self.getRestrictionError(containerHolder, Restriction.chargeGroup)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(chargeHolder, Restriction.chargeGroup)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(containerHolder)
        self.untrackHolder(chargeHolder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassMultiple(self):
        chargeItem = self.ch.type_(typeId=1, groupId=1008)
        chargeHolder = Mock(state=State.offline, item=chargeItem, _location=None, spec_set=Charge)
        containerItem = self.ch.type_(typeId=2, attributes={Attribute.chargeGroup3: 56, Attribute.chargeGroup5: 1008})
        containerHolder = Mock(state=State.offline, item=containerItem, _location=Location.ship, spec_set=Module)
        containerHolder.charge = chargeHolder
        chargeHolder.container = containerHolder
        self.trackHolder(containerHolder)
        self.trackHolder(chargeHolder)
        restrictionError1 = self.getRestrictionError(containerHolder, Restriction.chargeGroup)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(chargeHolder, Restriction.chargeGroup)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(containerHolder)
        self.untrackHolder(chargeHolder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassNoAttr(self):
        chargeItem = self.ch.type_(typeId=1, groupId=1008)
        chargeHolder = Mock(state=State.offline, item=chargeItem, _location=None, spec_set=Charge)
        containerItem = self.ch.type_(typeId=2, attributes={})
        containerHolder = Mock(state=State.offline, item=containerItem, _location=Location.ship, spec_set=Module)
        containerHolder.charge = chargeHolder
        chargeHolder.container = containerHolder
        self.trackHolder(containerHolder)
        self.trackHolder(chargeHolder)
        restrictionError1 = self.getRestrictionError(containerHolder, Restriction.chargeGroup)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(chargeHolder, Restriction.chargeGroup)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(containerHolder)
        self.untrackHolder(chargeHolder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()
