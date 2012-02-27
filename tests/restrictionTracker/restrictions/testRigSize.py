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


class TestRigSize(RestrictionTestCase):
    """Check functionality of rig size restriction"""

    def testFailMismatch(self):
        # Error should be raised when mismatching rig size
        # is added to ship
        fit = Fit()
        holder = IndependentItem(Type(None, attributes={Attribute.rigSize: 10}))
        fit.items.append(holder)
        ship = IndependentItem(Type(None, attributes={Attribute.rigSize: 6}))
        fit.ship = ship
        restrictionError = fit.getRestrictionError(holder, Restriction.rigSize)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.allowedSize, 6)
        self.assertEqual(restrictionError.holderSize, 10)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testFailOriginal(self):
        # Original value must be taken
        fit = Fit()
        holder = IndependentItem(Type(None, attributes={Attribute.rigSize: 10}))
        holder.attributes[Attribute.rigSize] = 5
        fit.items.append(holder)
        ship = IndependentItem(Type(None, attributes={Attribute.rigSize: 6}))
        ship.attributes[Attribute.rigSize] = 5
        fit.ship = ship
        restrictionError = fit.getRestrictionError(holder, Restriction.rigSize)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.allowedSize, 6)
        self.assertEqual(restrictionError.holderSize, 10)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testPassNoShip(self):
        # When no ship is assigned, no restriction
        # should be applied to ships
        fit = Fit()
        holder = IndependentItem(Type(None, attributes={Attribute.rigSize: 10}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.rigSize)
        self.assertIsNone(restrictionError)
        fit.items.remove(holder)
        self.assertBuffersEmpty(fit)

    def testPassShipNoAttr(self):
        # If ship doesn't have rig size attribute,
        # no restriction is applied onto rigs
        fit = Fit()
        holder = IndependentItem(Type(None, attributes={Attribute.rigSize: 10}))
        fit.items.append(holder)
        ship = IndependentItem(Type(None))
        fit.ship = ship
        restrictionError = fit.getRestrictionError(holder, Restriction.rigSize)
        self.assertIsNone(restrictionError)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testPassShipAttrNone(self):
        # If ship rig size attribute value is None,
        # no restriction is applied onto holders
        fit = Fit()
        holder = IndependentItem(Type(None, attributes={Attribute.rigSize: 10}))
        fit.items.append(holder)
        ship = IndependentItem(Type(None, attributes={Attribute.rigSize: None}))
        fit.ship = ship
        restrictionError = fit.getRestrictionError(holder, Restriction.rigSize)
        self.assertIsNone(restrictionError)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testPassHolderAttrNone(self):
        # Holders which have rig size specification None
        # are not subjects for restriction
        fit = Fit()
        holder = IndependentItem(Type(None, attributes={Attribute.rigSize: None}))
        fit.items.append(holder)
        ship = IndependentItem(Type(None, attributes={Attribute.rigSize: 6}))
        fit.ship = ship
        restrictionError = fit.getRestrictionError(holder, Restriction.rigSize)
        self.assertIsNone(restrictionError)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)
