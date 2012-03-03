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


class TestCalibration(RestrictionTestCase):
    """Check functionality of calibration restriction"""

    def testFailExcessNoShip(self):
        # Make sure error is raised on fits without ship
        fit = Fit()
        holder = IndependentItem(Type(None, attributes={Attribute.upgradeCost: 0}))
        holder.attributes[Attribute.upgradeCost] = 50
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.calibration)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.output, 0)
        self.assertEqual(restrictionError.totalUsage, 50)
        self.assertEqual(restrictionError.holderConsumption, 50)
        fit.items.remove(holder)
        self.assertBuffersEmpty(fit)

    def testFailExcessShipNoAttr(self):
        # When ship is assigned, but doesn't have calibration output
        # attribute, error should be raised for calibration consumers too
        fit = Fit()
        holder = IndependentItem(Type(None, attributes={Attribute.upgradeCost: 0}))
        holder.attributes[Attribute.upgradeCost] = 50
        fit.items.append(holder)
        ship = IndependentItem(Type(None))
        fit.ship = ship
        restrictionError = fit.getRestrictionError(holder, Restriction.calibration)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.output, 0)
        self.assertEqual(restrictionError.totalUsage, 50)
        self.assertEqual(restrictionError.holderConsumption, 50)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testFailExcessSingle(self):
        # When ship provides calibration output, but single consumer
        # demands for more, error should be raised
        fit = Fit()
        holder = IndependentItem(Type(None, attributes={Attribute.upgradeCost: 0}))
        holder.attributes[Attribute.upgradeCost] = 50
        fit.items.append(holder)
        ship = IndependentItem(Type(None))
        ship.attributes[Attribute.upgradeCapacity] = 40
        fit.ship = ship
        restrictionError = fit.getRestrictionError(holder, Restriction.calibration)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.output, 40)
        self.assertEqual(restrictionError.totalUsage, 50)
        self.assertEqual(restrictionError.holderConsumption, 50)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testFailExcessMultiple(self):
        # When multiple consumers require less than calibration output
        # alone, but in sum want more than total output, it should
        # be erroneous situation
        fit = Fit()
        holder1 = IndependentItem(Type(None, attributes={Attribute.upgradeCost: 0}))
        holder1.attributes[Attribute.upgradeCost] = 25
        fit.items.append(holder1)
        holder2 = IndependentItem(Type(None, attributes={Attribute.upgradeCost: 0}))
        holder2.attributes[Attribute.upgradeCost] = 20
        fit.items.append(holder2)
        ship = IndependentItem(Type(None))
        ship.attributes[Attribute.upgradeCapacity] = 40
        fit.ship = ship
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.calibration)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.output, 40)
        self.assertEqual(restrictionError1.totalUsage, 45)
        self.assertEqual(restrictionError1.holderConsumption, 25)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.calibration)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.output, 40)
        self.assertEqual(restrictionError2.totalUsage, 45)
        self.assertEqual(restrictionError2.holderConsumption, 20)
        fit.items.remove(holder1)
        fit.items.remove(holder2)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testFailExcessModified(self):
        # Make sure modified calibration values are taken
        fit = Fit()
        holder = IndependentItem(Type(None, attributes={Attribute.upgradeCost: 40}))
        holder.attributes[Attribute.upgradeCost] = 100
        fit.items.append(holder)
        ship = IndependentItem(Type(None, attributes={Attribute.upgradeCapacity: 45}))
        ship.attributes[Attribute.upgradeCapacity] = 50
        fit.ship = ship
        restrictionError = fit.getRestrictionError(holder, Restriction.calibration)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.output, 50)
        self.assertEqual(restrictionError.totalUsage, 100)
        self.assertEqual(restrictionError.holderConsumption, 100)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testMixUsageNegative(self):
        # If some holder has negative usage and calibration error is
        # still raised, check it's not raised for holder with
        # negative usage
        fit = Fit()
        holder1 = IndependentItem(Type(None, attributes={Attribute.upgradeCost: 0}))
        holder1.attributes[Attribute.upgradeCost] = 100
        fit.items.append(holder1)
        holder2 = IndependentItem(Type(None, attributes={Attribute.upgradeCost: 0}))
        holder2.attributes[Attribute.upgradeCost] = -10
        fit.items.append(holder2)
        ship = IndependentItem(Type(None))
        ship.attributes[Attribute.upgradeCapacity] = 50
        fit.ship = ship
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.calibration)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.output, 50)
        self.assertEqual(restrictionError1.totalUsage, 90)
        self.assertEqual(restrictionError1.holderConsumption, 100)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.calibration)
        self.assertIsNone(restrictionError2)
        fit.items.remove(holder1)
        fit.items.remove(holder2)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testMixUsageZero(self):
        # If some holder has zero usage and calibration error is
        # still raised, check it's not raised for holder with
        # zero usage
        fit = Fit()
        holder1 = IndependentItem(Type(None, attributes={Attribute.upgradeCost: 0}))
        holder1.attributes[Attribute.upgradeCost] = 100
        fit.items.append(holder1)
        holder2 = IndependentItem(Type(None, attributes={Attribute.upgradeCost: 0}))
        holder2.attributes[Attribute.upgradeCost] = 0
        fit.items.append(holder2)
        ship = IndependentItem(Type(None))
        ship.attributes[Attribute.upgradeCapacity] = 50
        fit.ship = ship
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.calibration)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.output, 50)
        self.assertEqual(restrictionError1.totalUsage, 100)
        self.assertEqual(restrictionError1.holderConsumption, 100)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.calibration)
        self.assertIsNone(restrictionError2)
        fit.items.remove(holder1)
        fit.items.remove(holder2)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testPass(self):
        # When total consumption is less than output,
        # no errors should be raised
        fit = Fit()
        holder1 = IndependentItem(Type(None, attributes={Attribute.upgradeCost: 0}))
        holder1.attributes[Attribute.upgradeCost] = 25
        fit.items.append(holder1)
        holder2 = IndependentItem(Type(None, attributes={Attribute.upgradeCost: 0}))
        holder2.attributes[Attribute.upgradeCost] = 20
        fit.items.append(holder2)
        ship = IndependentItem(Type(None))
        ship.attributes[Attribute.upgradeCapacity] = 50
        fit.ship = ship
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.calibration)
        self.assertIsNone(restrictionError1)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.calibration)
        self.assertIsNone(restrictionError2)
        fit.items.remove(holder1)
        fit.items.remove(holder2)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testPassNoOriginalAttr(self):
        # When added holder's item doesn't have original attribute,
        # holder shouldn't be tracked by register, and thus, no
        # errors should be raised
        fit = Fit()
        holder = IndependentItem(Type(None))
        holder.attributes[Attribute.upgradeCost] = 100
        fit.items.append(holder)
        ship = IndependentItem(Type(None))
        ship.attributes[Attribute.upgradeCapacity] = 50
        fit.ship = ship
        restrictionError = fit.getRestrictionError(holder, Restriction.calibration)
        self.assertIsNone(restrictionError)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testPassNegativeUse(self):
        # Check that even if use of one holder exceeds
        # calibration output, negative use of other holder may help
        # to avoid raising error
        fit = Fit()
        holder1 = IndependentItem(Type(None, attributes={Attribute.upgradeCost: 0}))
        holder1.attributes[Attribute.upgradeCost] = 50
        fit.items.append(holder1)
        holder2 = IndependentItem(Type(None, attributes={Attribute.upgradeCost: 0}))
        holder2.attributes[Attribute.upgradeCost] = -15
        fit.items.append(holder2)
        ship = IndependentItem(Type(None))
        ship.attributes[Attribute.upgradeCapacity] = 40
        fit.ship = ship
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.calibration)
        self.assertIsNone(restrictionError1)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.calibration)
        self.assertIsNone(restrictionError2)
        fit.items.remove(holder1)
        fit.items.remove(holder2)
        fit.ship = None
        self.assertBuffersEmpty(fit)
