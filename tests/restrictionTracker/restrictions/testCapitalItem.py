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
from eos.const.eve import Attribute, Type as ConstType
from eos.fit.holder.item import Module, Ship
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestCapitalItem(RestrictionTestCase):
    """Check functionality of capital-sized modules restriction"""

    def testFailNoShip(self):
        # Check that error is raised on attempt
        # to add capital item to fit w/o ship
        item = self.ch.type_(typeId=1, attributes={Attribute.volume: 501})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.capitalItem)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.allowedVolume, 500)
        self.assertEqual(restrictionError.holderVolume, 501)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailSubcapitalShip(self):
        # Check that error is raised on attempt
        # to add capital item to fit with subcapital
        # ship
        item = self.ch.type_(typeId=1, attributes={Attribute.volume: 501})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        shipItem = self.ch.type_(typeId=2)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        restrictionError = self.getRestrictionError(holder, Restriction.capitalItem)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.allowedVolume, 500)
        self.assertEqual(restrictionError.holderVolume, 501)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailOriginalVolume(self):
        # Make sure original volume value is taken
        item = self.ch.type_(typeId=1, attributes={Attribute.volume: 501})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        # Set volume below 500 to check that even when
        # modified attributes are available, raw attributes
        # are taken
        holder.attributes = {Attribute.volume: 100}
        self.trackHolder(holder)
        shipItem = self.ch.type_(typeId=2)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        restrictionError = self.getRestrictionError(holder, Restriction.capitalItem)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.allowedVolume, 500)
        self.assertEqual(restrictionError.holderVolume, 501)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassSubcapitalShipHolder(self):
        # Make sure no error raised when non-capital
        # item is added to fit
        item = self.ch.type_(typeId=1, attributes={Attribute.volume: 500})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.capitalItem)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassNonShipHolder(self):
        # Check that non-ship holders are not affected
        # by restriction
        item = self.ch.type_(typeId=1, attributes={Attribute.volume: 501})
        holder = Mock(state=State.offline, item=item, _location=None, spec_set=Ship)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.capitalItem)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassCapitalShip(self):
        # Check that capital holders can be added to
        # capital ship
        item = self.ch.type_(typeId=1, attributes={Attribute.volume: 501})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        shipItem = self.ch.type_(typeId=2)
        shipItem.requiredSkills = {ConstType.capitalShips: 1}
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        restrictionError = self.getRestrictionError(holder, Restriction.capitalItem)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassNoVolume(self):
        # Check that items with no volume attribute are not restricted
        item = self.ch.type_(typeId=1)
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        shipItem = self.ch.type_(typeId=2)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        restrictionError = self.getRestrictionError(holder, Restriction.capitalItem)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()
