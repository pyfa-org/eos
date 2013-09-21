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
from eos.fit.holder.item import Rig, Ship
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestRigSize(RestrictionTestCase):
    """Check functionality of rig size restriction"""

    def testFailMismatch(self):
        # Error should be raised when mismatching rig size
        # is added to ship
        item = self.ch.type_(typeId=1, attributes={Attribute.rigSize: 10})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Rig)
        self.trackHolder(holder)
        shipItem = self.ch.type_(typeId=2, attributes={Attribute.rigSize: 6})
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        self.setShip(shipHolder)
        restrictionError = self.getRestrictionError(holder, Restriction.rigSize)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.allowedSize, 6)
        self.assertEqual(restrictionError.holderSize, 10)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailOriginal(self):
        # Original value must be taken
        item = self.ch.type_(typeId=1, attributes={Attribute.rigSize: 10})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Rig)
        holder.attributes = {Attribute.rigSize: 5}
        self.trackHolder(holder)
        shipItem = self.ch.type_(typeId=2, attributes={Attribute.rigSize: 6})
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {Attribute.rigSize: 5}
        self.setShip(shipHolder)
        restrictionError = self.getRestrictionError(holder, Restriction.rigSize)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.allowedSize, 6)
        self.assertEqual(restrictionError.holderSize, 10)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassNoShip(self):
        # When no ship is assigned, no restriction
        # should be applied to ships
        item = self.ch.type_(typeId=1, attributes={Attribute.rigSize: 10})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Rig)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.rigSize)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassShipNoAttr(self):
        # If ship doesn't have rig size attribute,
        # no restriction is applied onto rigs
        item = self.ch.type_(typeId=1, attributes={Attribute.rigSize: 10})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Rig)
        self.trackHolder(holder)
        shipItem = self.ch.type_(typeId=2)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {}
        self.setShip(shipHolder)
        restrictionError = self.getRestrictionError(holder, Restriction.rigSize)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()
