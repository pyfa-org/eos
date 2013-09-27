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


class TestChargeSize(RestrictionTestCase):
    """Check functionality of charge size restriction"""

    def testFailLesser(self):
        chargeItem = self.ch.type_(typeId=1, attributes={Attribute.chargeSize: 2})
        chargeHolder = Mock(state=State.offline, item=chargeItem, _location=None, spec_set=Charge)
        containerItem = self.ch.type_(typeId=2, attributes={Attribute.chargeSize: 3})
        containerHolder = Mock(state=State.offline, item=containerItem, _location=Location.ship, spec_set=Module)
        containerHolder.charge = chargeHolder
        chargeHolder.container = containerHolder
        self.trackHolder(containerHolder)
        self.trackHolder(chargeHolder)
        restrictionError1 = self.getRestrictionError(containerHolder, Restriction.chargeSize)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(chargeHolder, Restriction.chargeSize)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.allowedSize, 3)
        self.assertEqual(restrictionError2.holderSize, 2)
        self.untrackHolder(containerHolder)
        self.untrackHolder(chargeHolder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailGreater(self):
        chargeItem = self.ch.type_(typeId=1, attributes={Attribute.chargeSize: 2})
        chargeHolder = Mock(state=State.offline, item=chargeItem, _location=None, spec_set=Charge)
        containerItem = self.ch.type_(typeId=2, attributes={Attribute.chargeSize: 1})
        containerHolder = Mock(state=State.offline, item=containerItem, _location=Location.ship, spec_set=Module)
        containerHolder.charge = chargeHolder
        chargeHolder.container = containerHolder
        self.trackHolder(containerHolder)
        self.trackHolder(chargeHolder)
        restrictionError1 = self.getRestrictionError(containerHolder, Restriction.chargeSize)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(chargeHolder, Restriction.chargeSize)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.allowedSize, 1)
        self.assertEqual(restrictionError2.holderSize, 2)
        self.untrackHolder(containerHolder)
        self.untrackHolder(chargeHolder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailChargeNoAttrib(self):
        chargeItem = self.ch.type_(typeId=1, attributes={})
        chargeHolder = Mock(state=State.offline, item=chargeItem, _location=None, spec_set=Charge)
        containerItem = self.ch.type_(typeId=2, attributes={Attribute.chargeSize: 3})
        containerHolder = Mock(state=State.offline, item=containerItem, _location=Location.ship, spec_set=Module)
        containerHolder.charge = chargeHolder
        chargeHolder.container = containerHolder
        self.trackHolder(containerHolder)
        self.trackHolder(chargeHolder)
        restrictionError1 = self.getRestrictionError(containerHolder, Restriction.chargeSize)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(chargeHolder, Restriction.chargeSize)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.allowedSize, 3)
        self.assertEqual(restrictionError2.holderSize, None)
        self.untrackHolder(containerHolder)
        self.untrackHolder(chargeHolder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassEqual(self):
        chargeItem = self.ch.type_(typeId=1, attributes={Attribute.chargeSize: 2})
        chargeHolder = Mock(state=State.offline, item=chargeItem, _location=None, spec_set=Charge)
        containerItem = self.ch.type_(typeId=2, attributes={Attribute.chargeSize: 2})
        containerHolder = Mock(state=State.offline, item=containerItem, _location=Location.ship, spec_set=Module)
        containerHolder.charge = chargeHolder
        chargeHolder.container = containerHolder
        self.trackHolder(containerHolder)
        self.trackHolder(chargeHolder)
        restrictionError1 = self.getRestrictionError(containerHolder, Restriction.chargeSize)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(chargeHolder, Restriction.chargeSize)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(containerHolder)
        self.untrackHolder(chargeHolder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassOriginalAttribs(self):
        # Make sure original item attributes are used
        chargeItem = self.ch.type_(typeId=1, attributes={Attribute.chargeSize: 2})
        chargeHolder = Mock(state=State.offline, item=chargeItem, _location=None, spec_set=Charge)
        chargeHolder.attributes = {Attribute.chargeSize: 1}
        containerItem = self.ch.type_(typeId=2, attributes={Attribute.chargeSize: 2})
        containerHolder = Mock(state=State.offline, item=containerItem, _location=Location.ship, spec_set=Module)
        containerHolder.attributes = {Attribute.chargeSize: 3}
        containerHolder.charge = chargeHolder
        chargeHolder.container = containerHolder
        self.trackHolder(containerHolder)
        self.trackHolder(chargeHolder)
        restrictionError1 = self.getRestrictionError(containerHolder, Restriction.chargeSize)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(chargeHolder, Restriction.chargeSize)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(containerHolder)
        self.untrackHolder(chargeHolder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassNoContainerAttrib(self):
        chargeItem = self.ch.type_(typeId=1, attributes={Attribute.chargeSize: 2})
        chargeHolder = Mock(state=State.offline, item=chargeItem, _location=None, spec_set=Charge)
        containerItem = self.ch.type_(typeId=2, attributes={})
        containerHolder = Mock(state=State.offline, item=containerItem, _location=Location.ship, spec_set=Module)
        containerHolder.charge = chargeHolder
        chargeHolder.container = containerHolder
        self.trackHolder(containerHolder)
        self.trackHolder(chargeHolder)
        restrictionError1 = self.getRestrictionError(containerHolder, Restriction.chargeSize)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(chargeHolder, Restriction.chargeSize)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(containerHolder)
        self.untrackHolder(chargeHolder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()
