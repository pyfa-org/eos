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


from eos.const import Restriction
from eos.eve.const import Attribute
from eos.eve.type import Type
from eos.tests.restrictionTracker.environment import Fit, IndependentItem
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestDroneGroup(RestrictionTestCase):
    """Check functionality of drone group restriction"""

    def testFailMismatch1(self):
        # Check that error is returned on attempt
        # to add drone from group mismatching to
        # first restriction attribute
        fit = Fit()
        holder = IndependentItem(Type(None, groupId=56))
        fit.drones.append(holder)
        fit.ship = IndependentItem(Type(None, attributes={Attribute.allowedDroneGroup1: 4}))
        restrictionError = fit.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedGroups, (4,))
        self.assertEqual(restrictionError.droneGroup, 56)
        fit.drones.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testFailMismatch2(self):
        # Check that error is returned on attempt
        # to add drone from group mismatching to
        # second restriction attribute
        fit = Fit()
        holder = IndependentItem(Type(None, groupId=797))
        fit.drones.append(holder)
        fit.ship = IndependentItem(Type(None, attributes={Attribute.allowedDroneGroup2: 69}))
        restrictionError = fit.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedGroups, (69,))
        self.assertEqual(restrictionError.droneGroup, 797)
        fit.drones.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testFailMismatchCombined(self):
        # Check that error is returned on attempt
        # to add drone from group mismatching to
        # both restriction attributes
        fit = Fit()
        holder = IndependentItem(Type(None, groupId=803))
        fit.drones.append(holder)
        fit.ship = IndependentItem(Type(None, attributes={Attribute.allowedDroneGroup1: 48, Attribute.allowedDroneGroup2: 106}))
        restrictionError = fit.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedGroups, (48, 106))
        self.assertEqual(restrictionError.droneGroup, 803)
        fit.drones.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testFailMismatchModified(self):
        # Check that error is returned on attempt
        # to add drone from group mismatching to
        # original restriction attribute, but matching
        # to modified restriction attribute. Effectively
        # we check that original attribute value is taken
        fit = Fit()
        holder = IndependentItem(Type(None, groupId=37))
        fit.drones.append(holder)
        ship = IndependentItem(Type(None, attributes={Attribute.allowedDroneGroup1: 59}))
        ship.attributes[Attribute.allowedDroneGroup1] = 37
        fit.ship = ship
        restrictionError = fit.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedGroups, (59,))
        self.assertEqual(restrictionError.droneGroup, 37)
        fit.drones.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testFailDroneNone(self):
        # Check that drone from None group is subject
        # to restriction
        fit = Fit()
        holder = IndependentItem(Type(None, groupId=None))
        fit.drones.append(holder)
        fit.ship = IndependentItem(Type(None, attributes={Attribute.allowedDroneGroup1: 1896}))
        restrictionError = fit.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedGroups, (1896,))
        self.assertEqual(restrictionError.droneGroup, None)
        fit.drones.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testPassNoShip(self):
        # Check that restriction isn't applied
        # when fit doesn't have ship
        fit = Fit()
        holder = IndependentItem(Type(None, groupId=None))
        fit.drones.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNone(restrictionError)
        fit.drones.remove(holder)
        self.assertBuffersEmpty(fit)

    def testPassShipNoRestriction(self):
        # Check that restriction isn't applied
        # when fit has ship, but without restriction
        # attribute
        fit = Fit()
        holder = IndependentItem(Type(None, groupId=71))
        fit.drones.append(holder)
        fit.ship = IndependentItem(Type(None))
        restrictionError = fit.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNone(restrictionError)
        fit.drones.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testPassNone(self):
        # Check that None-valued restriction attributes do
        # not affect anything
        fit = Fit()
        holder = IndependentItem(Type(80, groupId=None))
        fit.drones.append(holder)
        fit.ship = IndependentItem(Type(None, attributes={Attribute.allowedDroneGroup1: None, Attribute.allowedDroneGroup2: None}))
        restrictionError = fit.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNone(restrictionError)
        fit.drones.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)


    def testPassMatch1(self):
        # Check that no error raised when drone of group
        # matching to first restriction attribute is added
        fit = Fit()
        holder = IndependentItem(Type(None, groupId=22))
        fit.drones.append(holder)
        fit.ship = IndependentItem(Type(None, attributes={Attribute.allowedDroneGroup1: 22}))
        restrictionError = fit.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNone(restrictionError)
        fit.drones.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testPassMatch2(self):
        # Check that no error raised when drone of group
        # matching to second restriction attribute is added
        fit = Fit()
        holder = IndependentItem(Type(None, groupId=67))
        fit.drones.append(holder)
        fit.ship = IndependentItem(Type(None, attributes={Attribute.allowedDroneGroup2: 67}))
        restrictionError = fit.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNone(restrictionError)
        fit.drones.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testPassMatchCombination(self):
        # Check that no error raised when drone of group
        # matching to any of two restriction attributes
        # is added
        fit = Fit()
        holder = IndependentItem(Type(None, groupId=53))
        fit.drones.append(holder)
        fit.ship = IndependentItem(Type(None, attributes={Attribute.allowedDroneGroup1: 907, Attribute.allowedDroneGroup2: 53}))
        restrictionError = fit.getRestrictionError(holder, Restriction.droneGroup)
        self.assertIsNone(restrictionError)
        fit.drones.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)
