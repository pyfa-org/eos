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
from eos.eve.const import Attribute, Type as ConstType
from eos.eve.type import Type
from eos.tests.restrictionTracker.environment import Fit, IndependentItem, ShipItem
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestCapitalItem(RestrictionTestCase):
    """Check functionality of capital-sized modules restriction"""

    def testFailNoShip(self):
        fit = Fit()
        holder = ShipItem(Type(None, attributes={Attribute.volume: 501}))
        holder.state = State.offline
        fit._addHolder(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.capitalItem)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.allowedVolume, 500)
        self.assertEqual(restrictionError.holderVolume, 501)
        fit._removeHolder(holder)
        self.assertBuffersEmpty(fit)

    def testFailSubcapitalShip(self):
        fit = Fit()
        holder = ShipItem(Type(None, attributes={Attribute.volume: 501}))
        holder.state = State.offline
        fit._addHolder(holder)
        ship = IndependentItem(Type(None))
        fit.ship = ship
        fit._addHolder(ship)
        restrictionError = fit.getRestrictionError(holder, Restriction.capitalItem)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.allowedVolume, 500)
        self.assertEqual(restrictionError.holderVolume, 501)
        fit._removeHolder(holder)
        fit._removeHolder(ship)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testFailModifiedVolume(self):
        fit = Fit()
        holder = ShipItem(Type(None, attributes={Attribute.volume: 501}))
        holder.state = State.offline
        # Set volume below 500 to check that even when
        # modified attributes are available, raw attributes
        # are taken
        holder.attributes[Attribute.volume] = 100
        fit._addHolder(holder)
        ship = IndependentItem(Type(None))
        fit.ship = ship
        fit._addHolder(ship)
        restrictionError = fit.getRestrictionError(holder, Restriction.capitalItem)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.allowedVolume, 500)
        self.assertEqual(restrictionError.holderVolume, 501)
        fit._removeHolder(holder)
        fit._removeHolder(ship)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testPassSubcapitalShipHolder(self):
        fit = Fit()
        holder = ShipItem(Type(None, attributes={Attribute.volume: 500}))
        holder.state = State.offline
        fit._addHolder(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.capitalItem)
        self.assertIsNone(restrictionError)
        fit._removeHolder(holder)
        self.assertBuffersEmpty(fit)

    def testPassNonShipHolder(self):
        fit = Fit()
        holder = IndependentItem(Type(None, attributes={Attribute.volume: 501}))
        holder.state = State.offline
        fit._addHolder(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.capitalItem)
        self.assertIsNone(restrictionError)
        fit._removeHolder(holder)
        self.assertBuffersEmpty(fit)

    def testPassCapitalShip(self):
        fit = Fit()
        holder = ShipItem(Type(None, attributes={Attribute.volume: 501}))
        holder.state = State.offline
        fit._addHolder(holder)
        ship = IndependentItem(Type(None, attributes={Attribute.requiredSkill1: ConstType.capitalShips}))
        fit.ship = ship
        fit._addHolder(ship)
        restrictionError = fit.getRestrictionError(holder, Restriction.capitalItem)
        self.assertIsNone(restrictionError)
        fit._removeHolder(holder)
        fit._removeHolder(ship)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testPassNoneVolume(self):
        fit = Fit()
        holder = ShipItem(Type(None, attributes={Attribute.volume: None}))
        holder.state = State.offline
        fit._addHolder(holder)
        ship = IndependentItem(Type(None))
        fit.ship = ship
        fit._addHolder(ship)
        restrictionError = fit.getRestrictionError(holder, Restriction.capitalItem)
        self.assertIsNone(restrictionError)
        fit._removeHolder(holder)
        fit._removeHolder(ship)
        fit.ship = None
        self.assertBuffersEmpty(fit)
