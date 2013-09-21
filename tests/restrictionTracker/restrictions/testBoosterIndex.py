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
from eos.fit.holder.item import Booster, Module
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestBoosterIndex(RestrictionTestCase):
    """Check functionality of booster slot index restriction"""

    def testFail(self):
        # Check that if 2 or more holders are put into single slot
        # index, error is raised
        item = self.ch.type_(typeId=1, attributes={Attribute.boosterness: 120})
        holder1 = Mock(state=State.offline, item=item, _location=Location.character, spec_set=Booster)
        holder2 = Mock(state=State.offline, item=item, _location=Location.character, spec_set=Booster)
        self.trackHolder(holder1)
        self.trackHolder(holder2)
        restrictionError1 = self.getRestrictionError(holder1, Restriction.boosterIndex)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.holderSlotIndex, 120)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.boosterIndex)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.holderSlotIndex, 120)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailOtherHolderClass(self):
        # Make sure holders of all classes are affected
        item = self.ch.type_(typeId=1, attributes={Attribute.boosterness: 120})
        holder1 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        holder2 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder1)
        self.trackHolder(holder2)
        restrictionError1 = self.getRestrictionError(holder1, Restriction.boosterIndex)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.holderSlotIndex, 120)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.boosterIndex)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.holderSlotIndex, 120)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailOriginal(self):
        # Make sure that original attributes are used
        item = self.ch.type_(typeId=1, attributes={Attribute.boosterness: 120})
        holder1 = Mock(state=State.offline, item=item, _location=Location.character, spec_set=Booster)
        holder2 = Mock(state=State.offline, item=item, _location=Location.character, spec_set=Booster)
        holder1.attributes = {Attribute.boosterness: 119}
        holder2.attributes = {Attribute.boosterness: 121}
        self.trackHolder(holder1)
        self.trackHolder(holder2)
        restrictionError1 = self.getRestrictionError(holder1, Restriction.boosterIndex)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.holderSlotIndex, 120)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.boosterIndex)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.holderSlotIndex, 120)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPass(self):
        # Single holder which takes some slot shouldn't
        # trigger any errors
        item = self.ch.type_(typeId=1, attributes={Attribute.boosterness: 120})
        holder = Mock(state=State.offline, item=item, _location=Location.character, spec_set=Booster)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.boosterIndex)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassDifferent(self):
        # Holders taking different slots shouldn't trigger any errors
        item1 = self.ch.type_(typeId=1, attributes={Attribute.boosterness: 120})
        item2 = self.ch.type_(typeId=2, attributes={Attribute.boosterness: 121})
        holder1 = Mock(state=State.offline, item=item1, _location=Location.character, spec_set=Booster)
        holder2 = Mock(state=State.offline, item=item2, _location=Location.character, spec_set=Booster)
        self.trackHolder(holder1)
        self.trackHolder(holder2)
        restrictionError1 = self.getRestrictionError(holder1, Restriction.boosterIndex)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.boosterIndex)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()
