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


from eos.const.eos import State, Restriction
from eos.const.eve import Attribute
from eos.tests.restrictionTracker.environment import Fit, IndependentItem
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestLaunchedDrone(RestrictionTestCase):
    """Check functionality of max launched drone restriction"""

    def testFailExcessNoChar(self):
        # Check that any positive number of drones
        # results in error when no character is assigned
        # to fit
        fit = Fit()
        holder = IndependentItem(self.ch.type_(typeId=1))
        holder.state = State.online
        fit.drones.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.launchedDrone)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.maxLaunchedDrones, 0)
        self.assertEqual(restrictionError.launchedDrones, 1)
        fit.drones.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(fit)

    def testFailNoAttr(self):
        # Check that any positive number of drones
        # results in error when character is assigned
        # to fit, but no restriction attribute available
        fit = Fit()
        item = self.ch.type_(typeId=1)
        holder1 = IndependentItem(item)
        holder1.state = State.online
        fit.drones.append(holder1)
        holder2 = IndependentItem(item)
        holder2.state = State.online
        fit.drones.append(holder2)
        char = IndependentItem(self.ch.type_(typeId=2))
        char.attributes[Attribute.maxActiveDrones] = 1
        fit.character = char
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.launchedDrone)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.maxLaunchedDrones, 1)
        self.assertEqual(restrictionError1.launchedDrones, 2)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.launchedDrone)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.maxLaunchedDrones, 1)
        self.assertEqual(restrictionError2.launchedDrones, 2)
        fit.drones.remove(holder1)
        fit.drones.remove(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(fit)

    def testFailExcess(self):
        # Check that excessive number of drones results
        # in failure, even when character is assigned to
        # fit and max number attribute is available
        fit = Fit()
        item = self.ch.type_(typeId=1)
        holder1 = IndependentItem(item)
        holder1.state = State.online
        fit.drones.append(holder1)
        holder2 = IndependentItem(item)
        holder2.state = State.online
        fit.drones.append(holder2)
        char = IndependentItem(self.ch.type_(typeId=2))
        char.attributes[Attribute.maxActiveDrones] = 1
        fit.character = char
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.launchedDrone)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.maxLaunchedDrones, 1)
        self.assertEqual(restrictionError1.launchedDrones, 2)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.launchedDrone)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.maxLaunchedDrones, 1)
        self.assertEqual(restrictionError2.launchedDrones, 2)
        fit.drones.remove(holder1)
        fit.drones.remove(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(fit)

    def testFailExcessModified(self):
        # Check that modified attribute value is taken, not original
        fit = Fit()
        item = self.ch.type_(typeId=1)
        holder1 = IndependentItem(item)
        holder1.state = State.online
        fit.drones.append(holder1)
        holder2 = IndependentItem(item)
        holder2.state = State.online
        fit.drones.append(holder2)
        char = IndependentItem(self.ch.type_(typeId=2, attributes={Attribute.maxActiveDrones: 3}))
        char.attributes[Attribute.maxActiveDrones] = 1
        fit.character = char
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.launchedDrone)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.maxLaunchedDrones, 1)
        self.assertEqual(restrictionError1.launchedDrones, 2)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.launchedDrone)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.maxLaunchedDrones, 1)
        self.assertEqual(restrictionError2.launchedDrones, 2)
        fit.drones.remove(holder1)
        fit.drones.remove(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(fit)

    def testPass(self):
        # Check non-excessive number of drones
        fit = Fit()
        item = self.ch.type_(typeId=1)
        holder1 = IndependentItem(item)
        holder1.state = State.online
        fit.drones.append(holder1)
        holder2 = IndependentItem(item)
        holder2.state = State.online
        fit.drones.append(holder2)
        char = IndependentItem(self.ch.type_(typeId=2))
        char.attributes[Attribute.maxActiveDrones] = 5
        fit.character = char
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.launchedDrone)
        self.assertIsNone(restrictionError1)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.launchedDrone)
        self.assertIsNone(restrictionError2)
        fit.drones.remove(holder1)
        fit.drones.remove(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(fit)

    def testPassState(self):
        # Check excessive number of drones, which are
        # not 'launched'
        fit = Fit()
        item = self.ch.type_(typeId=1)
        holder1 = IndependentItem(item)
        fit.drones.append(holder1)
        holder2 = IndependentItem(item)
        fit.drones.append(holder2)
        char = IndependentItem(self.ch.type_(typeId=2))
        char.attributes[Attribute.maxActiveDrones] = 1
        fit.character = char
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.launchedDrone)
        self.assertIsNone(restrictionError1)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.launchedDrone)
        self.assertIsNone(restrictionError2)
        fit.drones.remove(holder1)
        fit.drones.remove(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(fit)

    def testPassNonDrone(self):
        # Check excessive number of non-drone items
        fit = Fit()
        item = self.ch.type_(typeId=1)
        holder1 = IndependentItem(item)
        holder1.state = State.online
        fit.items.append(holder1)
        holder2 = IndependentItem(item)
        holder2.state = State.online
        fit.items.append(holder2)
        char = IndependentItem(self.ch.type_(typeId=2))
        char.attributes[Attribute.maxActiveDrones] = 1
        fit.character = char
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.launchedDrone)
        self.assertIsNone(restrictionError1)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.launchedDrone)
        self.assertIsNone(restrictionError2)
        fit.items.remove(holder1)
        fit.items.remove(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(fit)
