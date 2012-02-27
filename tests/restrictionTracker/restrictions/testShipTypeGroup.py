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
from eos.tests.restrictionTracker.environment import Fit, IndependentItem, ShipItem
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestShipTypeGroup(RestrictionTestCase):
    """Check functionality of 'can fit to ship type/group' restriction"""

    def testFailType1(self):
        # Check that first type-restriction attribute affects
        # holder
        fit = Fit()
        ship = IndependentItem(Type(772, groupId=31))
        fit.ship = ship
        holder = ShipItem(Type(None, attributes={Attribute.canFitShipType1: 10}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedTypes, (10,))
        self.assertCountEqual(restrictionError.allowedGroups, ())
        self.assertEqual(restrictionError.shipType, 772)
        self.assertEqual(restrictionError.shipGroup, 31)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testFailType2(self):
        # Check that second type-restriction attribute affects
        # holder
        fit = Fit()
        ship = IndependentItem(Type(772, groupId=31))
        fit.ship = ship
        holder = ShipItem(Type(None, attributes={Attribute.canFitShipType2: 10}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedTypes, (10,))
        self.assertCountEqual(restrictionError.allowedGroups, ())
        self.assertEqual(restrictionError.shipType, 772)
        self.assertEqual(restrictionError.shipGroup, 31)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testFailType3(self):
        # Check that third type-restriction attribute affects
        # holder
        fit = Fit()
        ship = IndependentItem(Type(772, groupId=31))
        fit.ship = ship
        holder = ShipItem(Type(None, attributes={Attribute.canFitShipType3: 10}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedTypes, (10,))
        self.assertCountEqual(restrictionError.allowedGroups, ())
        self.assertEqual(restrictionError.shipType, 772)
        self.assertEqual(restrictionError.shipGroup, 31)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testFailType4(self):
        # Check that fourth type-restriction attribute affects
        # holder
        fit = Fit()
        ship = IndependentItem(Type(772, groupId=31))
        fit.ship = ship
        holder = ShipItem(Type(None, attributes={Attribute.canFitShipType4: 10}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedTypes, (10,))
        self.assertCountEqual(restrictionError.allowedGroups, ())
        self.assertEqual(restrictionError.shipType, 772)
        self.assertEqual(restrictionError.shipGroup, 31)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testFailType5(self):
        # Check that fifth type-restriction attribute affects
        # holder
        fit = Fit()
        ship = IndependentItem(Type(772, groupId=31))
        fit.ship = ship
        holder = ShipItem(Type(None, attributes={Attribute.fitsToShipType: 10}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedTypes, (10,))
        self.assertCountEqual(restrictionError.allowedGroups, ())
        self.assertEqual(restrictionError.shipType, 772)
        self.assertEqual(restrictionError.shipGroup, 31)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testFailGroup1(self):
        # Check that first group-restriction attribute affects
        # holder
        fit = Fit()
        ship = IndependentItem(Type(772, groupId=31))
        fit.ship = ship
        holder = ShipItem(Type(None, attributes={Attribute.canFitShipGroup1: 38}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedTypes, ())
        self.assertCountEqual(restrictionError.allowedGroups, (38,))
        self.assertEqual(restrictionError.shipType, 772)
        self.assertEqual(restrictionError.shipGroup, 31)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testFailGroup2(self):
        # Check that second group-restriction attribute affects
        # holder
        fit = Fit()
        ship = IndependentItem(Type(772, groupId=31))
        fit.ship = ship
        holder = ShipItem(Type(None, attributes={Attribute.canFitShipGroup2: 38}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedTypes, ())
        self.assertCountEqual(restrictionError.allowedGroups, (38,))
        self.assertEqual(restrictionError.shipType, 772)
        self.assertEqual(restrictionError.shipGroup, 31)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testFailGroup3(self):
        # Check that third group-restriction attribute affects
        # holder
        fit = Fit()
        ship = IndependentItem(Type(772, groupId=31))
        fit.ship = ship
        holder = ShipItem(Type(None, attributes={Attribute.canFitShipGroup3: 38}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedTypes, ())
        self.assertCountEqual(restrictionError.allowedGroups, (38,))
        self.assertEqual(restrictionError.shipType, 772)
        self.assertEqual(restrictionError.shipGroup, 31)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testFailGroup4(self):
        # Check that fourth group-restriction attribute affects
        # holder
        fit = Fit()
        ship = IndependentItem(Type(772, groupId=31))
        fit.ship = ship
        holder = ShipItem(Type(None, attributes={Attribute.canFitShipGroup4: 38}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedTypes, ())
        self.assertCountEqual(restrictionError.allowedGroups, (38,))
        self.assertEqual(restrictionError.shipType, 772)
        self.assertEqual(restrictionError.shipGroup, 31)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testFailCombined(self):
        # Check that failure is appropriately generated when
        # holder specifies both type and group restrictions
        fit = Fit()
        ship = IndependentItem(Type(772, groupId=31))
        fit.ship = ship
        holder = ShipItem(Type(None, attributes={Attribute.canFitShipType1: 1089, Attribute.canFitShipGroup1: 23}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedTypes, (1089,))
        self.assertCountEqual(restrictionError.allowedGroups, (23,))
        self.assertEqual(restrictionError.shipType, 772)
        self.assertEqual(restrictionError.shipGroup, 31)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testFailNoShip(self):
        # Absent ship should trigger this error too
        fit = Fit()
        holder = ShipItem(Type(None, attributes={Attribute.canFitShipType1: 10}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedTypes, (10,))
        self.assertCountEqual(restrictionError.allowedGroups, ())
        self.assertEqual(restrictionError.shipType, None)
        self.assertEqual(restrictionError.shipGroup, None)
        fit.items.remove(holder)
        self.assertBuffersEmpty(fit)

    def testFailAttrOriginal(self):
        # Make sure original value is taken
        fit = Fit()
        ship = IndependentItem(Type(772, groupId=31))
        fit.ship = ship
        holder = ShipItem(Type(None, attributes={Attribute.canFitShipType1: 10}))
        holder.attributes[Attribute.canFitShipType1] = 772
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError.allowedTypes, (10,))
        self.assertCountEqual(restrictionError.allowedGroups, ())
        self.assertEqual(restrictionError.shipType, 772)
        self.assertEqual(restrictionError.shipGroup, 31)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testPassTypeMatch(self):
        # When type of ship matches type-restriction attribute,
        # no error should be raised
        fit = Fit()
        ship = IndependentItem(Type(554, groupId=23))
        fit.ship = ship
        holder = ShipItem(Type(None, attributes={Attribute.canFitShipType1: 554}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNone(restrictionError)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testPassGroupMatch(self):
        # When type of ship matches group-restriction attribute,
        # no error should be raised
        fit = Fit()
        ship = IndependentItem(Type(554, groupId=23))
        fit.ship = ship
        holder = ShipItem(Type(None, attributes={Attribute.canFitShipGroup1: 23}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNone(restrictionError)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testPassCombinedMatch(self):
        # Check that it's enough to match any condition
        # to be fittable
        fit = Fit()
        ship = IndependentItem(Type(554, groupId=23))
        fit.ship = ship
        holder = ShipItem(Type(None, attributes={Attribute.canFitShipType1: 1089, Attribute.canFitShipGroup1: 23}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNone(restrictionError)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testPassHolderAttrNone(self):
        # When restriction attribute is None, it shouldn't
        # be taken into account
        fit = Fit()
        ship = IndependentItem(Type(772, groupId=31))
        fit.ship = ship
        holder = ShipItem(Type(None, attributes={Attribute.canFitShipType1: None}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNone(restrictionError)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testPassNonShipHolder(self):
        # Holders not belonging to ship shouldn't be affected
        fit = Fit()
        ship = IndependentItem(Type(772, groupId=31))
        fit.ship = ship
        holder = IndependentItem(Type(None, attributes={Attribute.canFitShipType1: 10}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.shipTypeGroup)
        self.assertIsNone(restrictionError)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)
