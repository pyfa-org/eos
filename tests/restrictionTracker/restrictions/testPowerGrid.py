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
from eos.fit.holder.item import Module, Implant
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestPowerGrid(RestrictionTestCase):
    """Check functionality of power grid restriction"""

    def testFailExcessSingle(self):
        # When ship provides pg output, but single consumer
        # demands for more, error should be raised
        item = self.ch.type_(typeId=1, attributes={Attribute.power: 0})
        holder = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder.attributes = {Attribute.power: 50}
        self.trackHolder(holder)
        self.fit.stats.powerGrid.used = 50
        self.fit.stats.powerGrid.output = 40
        restrictionError = self.getRestrictionError(holder, Restriction.powerGrid)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.output, 40)
        self.assertEqual(restrictionError.totalUse, 50)
        self.assertEqual(restrictionError.holderUse, 50)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailExcessSingleOtherClassLocation(self):
        # Make sure holders of all classes are affected
        item = self.ch.type_(typeId=1, attributes={Attribute.power: 0})
        holder = Mock(state=State.online, item=item, _location=Location.character, spec_set=Implant)
        holder.attributes = {Attribute.power: 50}
        self.trackHolder(holder)
        self.fit.stats.powerGrid.used = 50
        self.fit.stats.powerGrid.output = 40
        restrictionError = self.getRestrictionError(holder, Restriction.powerGrid)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.output, 40)
        self.assertEqual(restrictionError.totalUse, 50)
        self.assertEqual(restrictionError.holderUse, 50)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailExcessSingleUndefinedOutput(self):
        # When stats module does not specify output, make sure
        # it's assumed to be 0
        item = self.ch.type_(typeId=1, attributes={Attribute.power: 0})
        holder = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder.attributes = {Attribute.power: 5}
        self.trackHolder(holder)
        self.fit.stats.powerGrid.used = 5
        self.fit.stats.powerGrid.output = None
        restrictionError = self.getRestrictionError(holder, Restriction.powerGrid)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.output, 0)
        self.assertEqual(restrictionError.totalUse, 5)
        self.assertEqual(restrictionError.holderUse, 5)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailExcessMultiple(self):
        # When multiple consumers require less than pg output
        # alone, but in sum want more than total output, it should
        # be erroneous situation
        item = self.ch.type_(typeId=1, attributes={Attribute.power: 0})
        holder1 = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder1.attributes = {Attribute.power: 25}
        self.trackHolder(holder1)
        holder2 = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder2.attributes = {Attribute.power: 20}
        self.trackHolder(holder2)
        self.fit.stats.powerGrid.used = 45
        self.fit.stats.powerGrid.output = 40
        restrictionError1 = self.getRestrictionError(holder1, Restriction.powerGrid)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.output, 40)
        self.assertEqual(restrictionError1.totalUse, 45)
        self.assertEqual(restrictionError1.holderUse, 25)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.powerGrid)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.output, 40)
        self.assertEqual(restrictionError2.totalUse, 45)
        self.assertEqual(restrictionError2.holderUse, 20)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailExcessModified(self):
        # Make sure modified pg values are taken
        item = self.ch.type_(typeId=1, attributes={Attribute.power: 40})
        holder = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder.attributes = {Attribute.power: 100}
        self.trackHolder(holder)
        self.fit.stats.powerGrid.used = 100
        self.fit.stats.powerGrid.output = 50
        restrictionError = self.getRestrictionError(holder, Restriction.powerGrid)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.output, 50)
        self.assertEqual(restrictionError.totalUse, 100)
        self.assertEqual(restrictionError.holderUse, 100)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testMixUsageNegative(self):
        # If some holder has negative usage and pg error is
        # still raised, check it's not raised for holder with
        # negative usage
        item = self.ch.type_(typeId=1, attributes={Attribute.power: 0})
        holder1 = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder1.attributes = {Attribute.power: 100}
        self.trackHolder(holder1)
        holder2 = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder2.attributes = {Attribute.power: -10}
        self.trackHolder(holder2)
        self.fit.stats.powerGrid.used = 90
        self.fit.stats.powerGrid.output = 50
        restrictionError1 = self.getRestrictionError(holder1, Restriction.powerGrid)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.output, 50)
        self.assertEqual(restrictionError1.totalUse, 90)
        self.assertEqual(restrictionError1.holderUse, 100)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.powerGrid)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testMixUsageZero(self):
        # If some holder has zero usage and pg error is
        # still raised, check it's not raised for holder with
        # zero usage
        item = self.ch.type_(typeId=1, attributes={Attribute.power: 0})
        holder1 = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder1.attributes = {Attribute.power: 100}
        self.trackHolder(holder1)
        holder2 = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder2.attributes = {Attribute.power: 0}
        self.trackHolder(holder2)
        self.fit.stats.powerGrid.used = 100
        self.fit.stats.powerGrid.output = 50
        restrictionError1 = self.getRestrictionError(holder1, Restriction.powerGrid)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.output, 50)
        self.assertEqual(restrictionError1.totalUse, 100)
        self.assertEqual(restrictionError1.holderUse, 100)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.powerGrid)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPass(self):
        # When total consumption is less than output,
        # no errors should be raised
        item = self.ch.type_(typeId=1, attributes={Attribute.power: 0})
        holder1 = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder1.attributes = {Attribute.power: 25}
        self.trackHolder(holder1)
        holder2 = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder2.attributes = {Attribute.power: 20}
        self.trackHolder(holder2)
        self.fit.stats.powerGrid.used = 45
        self.fit.stats.powerGrid.output = 50
        restrictionError1 = self.getRestrictionError(holder1, Restriction.powerGrid)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(holder2, Restriction.powerGrid)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassNoOriginalAttr(self):
        # When added holder's item doesn't have original attribute,
        # holder shouldn't be tracked by register, and thus, no
        # errors should be raised
        item = self.ch.type_(typeId=1)
        holder = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder.attributes = {Attribute.power: 100}
        self.trackHolder(holder)
        self.fit.stats.powerGrid.used = 100
        self.fit.stats.powerGrid.output = 50
        restrictionError = self.getRestrictionError(holder, Restriction.powerGrid)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassState(self):
        # When holder isn't online, it shouldn't consume anything
        item = self.ch.type_(typeId=1, attributes={Attribute.power: 0})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        holder.attributes = {Attribute.power: 50}
        self.trackHolder(holder)
        self.fit.stats.powerGrid.used = 50
        self.fit.stats.powerGrid.output = 40
        restrictionError = self.getRestrictionError(holder, Restriction.powerGrid)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()
