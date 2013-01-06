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


from eos.const import Restriction
from eos.eve.const import Attribute, Type as ConstType
from eos.tests.restrictionTracker.environment import Fit, IndependentItem, ShipItem
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestCapitalItem(RestrictionTestCase):
    """Check functionality of capital-sized modules restriction"""

    def testFailNoShip(self):
        # Check that error is raised on attempt
        # to add capital item to fit w/o ship
        fit = Fit()
        holder = ShipItem(self.ch.type_(typeId=1, attributes={Attribute.volume: 501}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.capitalItem)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.allowedVolume, 500)
        self.assertEqual(restrictionError.holderVolume, 501)
        fit.items.remove(holder)
        self.assertBuffersEmpty(fit)

    def testFailSubcapitalShip(self):
        # Check that error is raised on attempt
        # to add capital item to fit with subcapital
        # ship
        fit = Fit()
        holder = ShipItem(self.ch.type_(typeId=1, attributes={Attribute.volume: 501}))
        fit.items.append(holder)
        fit.ship = IndependentItem(self.ch.type_(typeId=2))
        restrictionError = fit.getRestrictionError(holder, Restriction.capitalItem)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.allowedVolume, 500)
        self.assertEqual(restrictionError.holderVolume, 501)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testFailOriginalVolume(self):
        # Make sure original volume value is taken
        fit = Fit()
        holder = ShipItem(self.ch.type_(typeId=1, attributes={Attribute.volume: 501}))
        # Set volume below 500 to check that even when
        # modified attributes are available, raw attributes
        # are taken
        holder.attributes[Attribute.volume] = 100
        fit.items.append(holder)
        fit.ship = IndependentItem(self.ch.type_(typeId=2))
        restrictionError = fit.getRestrictionError(holder, Restriction.capitalItem)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.allowedVolume, 500)
        self.assertEqual(restrictionError.holderVolume, 501)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testPassSubcapitalShipHolder(self):
        # Make sure no error raised when non-capital
        # item is added to fit
        fit = Fit()
        holder = ShipItem(self.ch.type_(typeId=1, attributes={Attribute.volume: 500}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.capitalItem)
        self.assertIsNone(restrictionError)
        fit.items.remove(holder)
        self.assertBuffersEmpty(fit)

    def testPassNonShipHolder(self):
        # Check that non-ship holders are not affected
        # by restriction
        fit = Fit()
        holder = IndependentItem(self.ch.type_(typeId=1, attributes={Attribute.volume: 501}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.capitalItem)
        self.assertIsNone(restrictionError)
        fit.items.remove(holder)
        self.assertBuffersEmpty(fit)

    def testPassCapitalShip(self):
        # Check that capital holders can be added to
        # capital ship
        fit = Fit()
        holder = ShipItem(self.ch.type_(typeId=1, attributes={Attribute.volume: 501}))
        fit.items.append(holder)
        shipItem = self.ch.type_(typeId=2)
        shipItem.requiredSkills = {ConstType.capitalShips: 1}
        fit.ship = IndependentItem(shipItem)
        restrictionError = fit.getRestrictionError(holder, Restriction.capitalItem)
        self.assertIsNone(restrictionError)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testPassNoVolume(self):
        # Check that items with no volume attribute are not restricted
        fit = Fit()
        holder = ShipItem(self.ch.type_(typeId=1))
        fit.items.append(holder)
        fit.ship = IndependentItem(self.ch.type_(typeId=2))
        restrictionError = fit.getRestrictionError(holder, Restriction.capitalItem)
        self.assertIsNone(restrictionError)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)
