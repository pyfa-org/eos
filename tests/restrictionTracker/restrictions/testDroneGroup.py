#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2012 Anton Vorobyov
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


from eos.const import State, Restriction
from eos.eve.const import Attribute
from eos.eve.type import Type
from eos.tests.restrictionTracker.environment import Fit, IndependentItem
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestDroneGroup(RestrictionTestCase):
    """Check functionality of drone group restriction"""

    def testFailMismatch1(self):
        fit = Fit()
        holder = IndependentItem(Type(None, groupId=56))
        holder.state = State.offline
        fit.drones.append(holder)
        fit._addHolder(holder)
        ship = IndependentItem(Type(None, attributes={Attribute.allowedDroneGroup1: 4}))
        fit.ship = ship
        fit._addHolder(ship)
        restrictionError = fit.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedGroups, (4,))
        self.assertEqual(restrictionError.droneGroup, 56)
        fit._removeHolder(holder)
        fit.drones.remove(holder)
        fit._removeHolder(ship)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testFailMismatch2(self):
        fit = Fit()
        holder = IndependentItem(Type(None, groupId=797))
        holder.state = State.offline
        fit.drones.append(holder)
        fit._addHolder(holder)
        ship = IndependentItem(Type(None, attributes={Attribute.allowedDroneGroup2: 69}))
        fit.ship = ship
        fit._addHolder(ship)
        restrictionError = fit.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedGroups, (69,))
        self.assertEqual(restrictionError.droneGroup, 797)
        fit._removeHolder(holder)
        fit.drones.remove(holder)
        fit._removeHolder(ship)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testFailMismatchCombined(self):
        fit = Fit()
        holder = IndependentItem(Type(None, groupId=803))
        holder.state = State.offline
        fit.drones.append(holder)
        fit._addHolder(holder)
        ship = IndependentItem(Type(None, attributes={Attribute.allowedDroneGroup1: 48, Attribute.allowedDroneGroup2: 106}))
        fit.ship = ship
        fit._addHolder(ship)
        restrictionError = fit.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedGroups, (48, 106))
        self.assertEqual(restrictionError.droneGroup, 803)
        fit._removeHolder(holder)
        fit.drones.remove(holder)
        fit._removeHolder(ship)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testFailMismatchModified(self):
        fit = Fit()
        holder = IndependentItem(Type(None, groupId=37))
        holder.state = State.offline
        fit.drones.append(holder)
        fit._addHolder(holder)
        ship = IndependentItem(Type(None, attributes={Attribute.allowedDroneGroup1: 59}))
        ship.attributes = {Attribute.allowedDroneGroup1: 37}
        fit.ship = ship
        fit._addHolder(ship)
        restrictionError = fit.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedGroups, (59,))
        self.assertEqual(restrictionError.droneGroup, 37)
        fit._removeHolder(holder)
        fit.drones.remove(holder)
        fit._removeHolder(ship)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testFailAllowedNone(self):
        fit = Fit()
        holder = IndependentItem(Type(None, groupId=408))
        holder.state = State.offline
        fit.drones.append(holder)
        fit._addHolder(holder)
        ship = IndependentItem(Type(None, attributes={Attribute.allowedDroneGroup1: None, Attribute.allowedDroneGroup2: None}))
        fit.ship = ship
        fit._addHolder(ship)
        restrictionError = fit.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedGroups, ())
        self.assertEqual(restrictionError.droneGroup, 408)
        fit._removeHolder(holder)
        fit.drones.remove(holder)
        fit._removeHolder(ship)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testFailDroneNone(self):
        fit = Fit()
        holder = IndependentItem(Type(None, groupId=None))
        holder.state = State.offline
        fit.drones.append(holder)
        fit._addHolder(holder)
        ship = IndependentItem(Type(None, attributes={Attribute.allowedDroneGroup1: 1896}))
        fit.ship = ship
        fit._addHolder(ship)
        restrictionError = fit.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedGroups, (1896,))
        self.assertEqual(restrictionError.droneGroup, None)
        fit._removeHolder(holder)
        fit.drones.remove(holder)
        fit._removeHolder(ship)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testPassNoShip(self):
        fit = Fit()
        holder = IndependentItem(Type(None, groupId=None))
        holder.state = State.offline
        fit.drones.append(holder)
        fit._addHolder(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNone(restrictionError)
        fit._removeHolder(holder)
        fit.drones.remove(holder)
        self.assertBuffersEmpty(fit)

    def testPassShipNoRestriction(self):
        fit = Fit()
        holder = IndependentItem(Type(None, groupId=71))
        holder.state = State.offline
        fit.drones.append(holder)
        fit._addHolder(holder)
        ship = IndependentItem(Type(None))
        fit.ship = ship
        fit._addHolder(ship)
        restrictionError = fit.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNone(restrictionError)
        fit._removeHolder(holder)
        fit.drones.remove(holder)
        fit._removeHolder(ship)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testPassMatch1(self):
        fit = Fit()
        holder = IndependentItem(Type(None, groupId=22))
        holder.state = State.offline
        fit.drones.append(holder)
        fit._addHolder(holder)
        ship = IndependentItem(Type(None, attributes={Attribute.allowedDroneGroup1: 22}))
        fit.ship = ship
        fit._addHolder(ship)
        restrictionError = fit.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNone(restrictionError)
        fit._removeHolder(holder)
        fit.drones.remove(holder)
        fit._removeHolder(ship)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testPassMatch2(self):
        fit = Fit()
        holder = IndependentItem(Type(None, groupId=67))
        holder.state = State.offline
        fit.drones.append(holder)
        fit._addHolder(holder)
        ship = IndependentItem(Type(None, attributes={Attribute.allowedDroneGroup2: 67}))
        fit.ship = ship
        fit._addHolder(ship)
        restrictionError = fit.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNone(restrictionError)
        fit._removeHolder(holder)
        fit.drones.remove(holder)
        fit._removeHolder(ship)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testPassMatchCombination(self):
        fit = Fit()
        holder = IndependentItem(Type(None, groupId=53))
        holder.state = State.offline
        fit.drones.append(holder)
        fit._addHolder(holder)
        ship = IndependentItem(Type(None, attributes={Attribute.allowedDroneGroup1: 907, Attribute.allowedDroneGroup2: 53}))
        fit.ship = ship
        fit._addHolder(ship)
        restrictionError = fit.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNone(restrictionError)
        fit._removeHolder(holder)
        fit.drones.remove(holder)
        fit._removeHolder(ship)
        fit.ship = None
        self.assertBuffersEmpty(fit)
