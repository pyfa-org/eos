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


from eos.const import State, Restriction
from eos.eve.const import Attribute
from eos.tests.restrictionTracker.environment import Fit, IndependentItem
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestPowerGrid(RestrictionTestCase):
    """Check functionality of power grid restriction"""

    def testFailExcessNoShip(self):
        # Make sure error is raised on fits without ship
        fit = Fit()
        holder = IndependentItem(self.ch.type_(typeId=1, attributes={Attribute.power: 0}))
        holder.attributes[Attribute.power] = 50
        holder.state = State.online
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.powerGrid)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.output, 0)
        self.assertEqual(restrictionError.totalUsage, 50)
        self.assertEqual(restrictionError.holderConsumption, 50)
        fit.items.remove(holder)
        self.assertBuffersEmpty(fit)

    def testFailExcessShipNoAttr(self):
        # When ship is assigned, but doesn't have power grid output
        # attribute, error should be raised for power grid consumers too
        fit = Fit()
        holder = IndependentItem(self.ch.type_(typeId=1, attributes={Attribute.power: 0}))
        holder.attributes[Attribute.power] = 50
        holder.state = State.online
        fit.items.append(holder)
        ship = IndependentItem(self.ch.type_(typeId=2))
        fit.ship = ship
        restrictionError = fit.getRestrictionError(holder, Restriction.powerGrid)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.output, 0)
        self.assertEqual(restrictionError.totalUsage, 50)
        self.assertEqual(restrictionError.holderConsumption, 50)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testFailExcessSingle(self):
        # When ship provides power grid output, but single consumer
        # demands for more, error should be raised
        fit = Fit()
        holder = IndependentItem(self.ch.type_(typeId=1, attributes={Attribute.power: 0}))
        holder.attributes[Attribute.power] = 50
        holder.state = State.online
        fit.items.append(holder)
        ship = IndependentItem(self.ch.type_(typeId=2))
        ship.attributes[Attribute.powerOutput] = 40
        fit.ship = ship
        restrictionError = fit.getRestrictionError(holder, Restriction.powerGrid)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.output, 40)
        self.assertEqual(restrictionError.totalUsage, 50)
        self.assertEqual(restrictionError.holderConsumption, 50)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testFailExcessMultiple(self):
        # When multiple consumers require less than power grid output
        # alone, but in sum want more than total output, it should
        # be erroneous situation
        fit = Fit()
        item = self.ch.type_(typeId=1, attributes={Attribute.power: 0})
        holder1 = IndependentItem(item)
        holder1.attributes[Attribute.power] = 25
        holder1.state = State.online
        fit.items.append(holder1)
        holder2 = IndependentItem(item)
        holder2.attributes[Attribute.power] = 20
        holder2.state = State.online
        fit.items.append(holder2)
        ship = IndependentItem(self.ch.type_(typeId=2))
        ship.attributes[Attribute.powerOutput] = 40
        fit.ship = ship
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.powerGrid)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.output, 40)
        self.assertEqual(restrictionError1.totalUsage, 45)
        self.assertEqual(restrictionError1.holderConsumption, 25)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.powerGrid)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.output, 40)
        self.assertEqual(restrictionError2.totalUsage, 45)
        self.assertEqual(restrictionError2.holderConsumption, 20)
        fit.items.remove(holder1)
        fit.items.remove(holder2)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testFailExcessModified(self):
        # Make sure modified power grid values are taken
        fit = Fit()
        holder = IndependentItem(self.ch.type_(typeId=1, attributes={Attribute.power: 40}))
        holder.attributes[Attribute.power] = 100
        holder.state = State.online
        fit.items.append(holder)
        ship = IndependentItem(self.ch.type_(typeId=2, attributes={Attribute.powerOutput: 45}))
        ship.attributes[Attribute.powerOutput] = 50
        fit.ship = ship
        restrictionError = fit.getRestrictionError(holder, Restriction.powerGrid)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.output, 50)
        self.assertEqual(restrictionError.totalUsage, 100)
        self.assertEqual(restrictionError.holderConsumption, 100)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testMixUsageNegative(self):
        # If some holder has negative usage and power grid error is
        # still raised, check it's not raised for holder with
        # negative usage
        fit = Fit()
        item = self.ch.type_(typeId=1, attributes={Attribute.power: 0})
        holder1 = IndependentItem(item)
        holder1.attributes[Attribute.power] = 100
        holder1.state = State.online
        fit.items.append(holder1)
        holder2 = IndependentItem(item)
        holder2.attributes[Attribute.power] = -10
        holder2.state = State.online
        fit.items.append(holder2)
        ship = IndependentItem(self.ch.type_(typeId=2))
        ship.attributes[Attribute.powerOutput] = 50
        fit.ship = ship
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.powerGrid)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.output, 50)
        self.assertEqual(restrictionError1.totalUsage, 90)
        self.assertEqual(restrictionError1.holderConsumption, 100)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.powerGrid)
        self.assertIsNone(restrictionError2)
        fit.items.remove(holder1)
        fit.items.remove(holder2)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testMixUsageZero(self):
        # If some holder has zero usage and power grid error is
        # still raised, check it's not raised for holder with
        # zero usage
        fit = Fit()
        item = self.ch.type_(typeId=1, attributes={Attribute.power: 0})
        holder1 = IndependentItem(item)
        holder1.attributes[Attribute.power] = 100
        holder1.state = State.online
        fit.items.append(holder1)
        holder2 = IndependentItem(item)
        holder2.attributes[Attribute.power] = 0
        holder2.state = State.online
        fit.items.append(holder2)
        ship = IndependentItem(self.ch.type_(typeId=2))
        ship.attributes[Attribute.powerOutput] = 50
        fit.ship = ship
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.powerGrid)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.output, 50)
        self.assertEqual(restrictionError1.totalUsage, 100)
        self.assertEqual(restrictionError1.holderConsumption, 100)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.powerGrid)
        self.assertIsNone(restrictionError2)
        fit.items.remove(holder1)
        fit.items.remove(holder2)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testPass(self):
        # When total consumption is less than output,
        # no errors should be raised
        fit = Fit()
        item = self.ch.type_(typeId=1, attributes={Attribute.power: 0})
        holder1 = IndependentItem(item)
        holder1.attributes[Attribute.power] = 25
        holder1.state = State.online
        fit.items.append(holder1)
        holder2 = IndependentItem(item)
        holder2.attributes[Attribute.power] = 20
        holder2.state = State.online
        fit.items.append(holder2)
        ship = IndependentItem(self.ch.type_(typeId=2))
        ship.attributes[Attribute.powerOutput] = 50
        fit.ship = ship
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.powerGrid)
        self.assertIsNone(restrictionError1)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.powerGrid)
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
        holder = IndependentItem(self.ch.type_(typeId=1))
        holder.attributes[Attribute.power] = 100
        holder.state = State.online
        fit.items.append(holder)
        ship = IndependentItem(self.ch.type_(typeId=2))
        ship.attributes[Attribute.powerOutput] = 50
        fit.ship = ship
        restrictionError = fit.getRestrictionError(holder, Restriction.powerGrid)
        self.assertIsNone(restrictionError)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testPassNegativeUse(self):
        # Check that even if use of one holder exceeds
        # power grid output, negative use of other holder may help
        # to avoid raising error
        fit = Fit()
        item = self.ch.type_(typeId=1, attributes={Attribute.power: 0})
        holder1 = IndependentItem(item)
        holder1.attributes[Attribute.power] = 50
        holder1.state = State.online
        fit.items.append(holder1)
        holder2 = IndependentItem(item)
        holder2.attributes[Attribute.power] = -15
        holder2.state = State.online
        fit.items.append(holder2)
        ship = IndependentItem(self.ch.type_(typeId=2))
        ship.attributes[Attribute.powerOutput] = 40
        fit.ship = ship
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.powerGrid)
        self.assertIsNone(restrictionError1)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.powerGrid)
        self.assertIsNone(restrictionError2)
        fit.items.remove(holder1)
        fit.items.remove(holder2)
        fit.ship = None
        self.assertBuffersEmpty(fit)

    def testPassState(self):
        # When holder isn't online, it shouldn't consume anything
        fit = Fit()
        holder = IndependentItem(self.ch.type_(typeId=1, attributes={Attribute.power: 0}))
        holder.attributes[Attribute.power] = 50
        fit.items.append(holder)
        ship = IndependentItem(self.ch.type_(typeId=2))
        ship.attributes[Attribute.powerOutput] = 40
        fit.ship = ship
        restrictionError = fit.getRestrictionError(holder, Restriction.powerGrid)
        self.assertIsNone(restrictionError)
        fit.items.remove(holder)
        fit.ship = None
        self.assertBuffersEmpty(fit)
