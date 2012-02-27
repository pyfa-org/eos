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
from eos.tests.restrictionTracker.environment import Fit, IndependentItem, ShipItem
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestMaxGroupOnline(RestrictionTestCase):
    """Check functionality of max group online restriction"""

    def testFailExcessAll(self):
        # Make sure error is raised for all holders exceeding
        # their group restriction
        fit = Fit()
        holder1 = ShipItem(Type(None, groupId=6, attributes={Attribute.maxGroupOnline: 1}))
        holder1.state = State.online
        fit.items.append(holder1)
        holder2 = ShipItem(Type(None, groupId=6, attributes={Attribute.maxGroupOnline: 1}))
        holder2.state = State.online
        fit.items.append(holder2)
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.maxGroupOnline)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.maxGroup, 1)
        self.assertEqual(restrictionError1.holderGroup, 6)
        self.assertEqual(restrictionError1.groupHolders, 2)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.maxGroupOnline)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.maxGroup, 1)
        self.assertEqual(restrictionError2.holderGroup, 6)
        self.assertEqual(restrictionError2.groupHolders, 2)
        fit.items.remove(holder1)
        fit.items.remove(holder2)
        self.assertBuffersEmpty(fit)

    def testMixExcessOne(self):
        # Make sure error is raised for just holders which excess
        # restriction,even if they're from the same group
        fit = Fit()
        holder1 = ShipItem(Type(None, groupId=92, attributes={Attribute.maxGroupOnline: 1}))
        holder1.state = State.online
        fit.items.append(holder1)
        holder2 = ShipItem(Type(None, groupId=92, attributes={Attribute.maxGroupOnline: 2}))
        holder2.state = State.online
        fit.items.append(holder2)
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.maxGroupOnline)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.maxGroup, 1)
        self.assertEqual(restrictionError1.holderGroup, 92)
        self.assertEqual(restrictionError1.groupHolders, 2)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.maxGroupOnline)
        self.assertIsNone(restrictionError2)
        fit.items.remove(holder1)
        fit.items.remove(holder2)
        self.assertBuffersEmpty(fit)

    def testMixExcessOriginal(self):
        # Check that original item attributes are used
        fit = Fit()
        holder1 = ShipItem(Type(None, groupId=61, attributes={Attribute.maxGroupOnline: 1}))
        holder1.attributes[Attribute.maxGroupOnline] = 2
        holder1.state = State.online
        fit.items.append(holder1)
        holder2 = ShipItem(Type(None, groupId=61, attributes={Attribute.maxGroupOnline: 2}))
        holder2.attributes[Attribute.maxGroupOnline] = 1
        holder2.state = State.online
        fit.items.append(holder2)
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.maxGroupOnline)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.maxGroup, 1)
        self.assertEqual(restrictionError1.holderGroup, 61)
        self.assertEqual(restrictionError1.groupHolders, 2)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.maxGroupOnline)
        self.assertIsNone(restrictionError2)
        fit.items.remove(holder1)
        fit.items.remove(holder2)
        self.assertBuffersEmpty(fit)

    def testPass(self):
        # Make sure no errors are raised when number of added
        # items doesn't exceed any restrictions
        fit = Fit()
        holder1 = ShipItem(Type(None, groupId=860, attributes={Attribute.maxGroupOnline: 2}))
        holder1.state = State.online
        fit.items.append(holder1)
        holder2 = ShipItem(Type(None, groupId=860, attributes={Attribute.maxGroupOnline: 2}))
        holder2.state = State.online
        fit.items.append(holder2)
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.maxGroupOnline)
        self.assertIsNone(restrictionError1)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.maxGroupOnline)
        self.assertIsNone(restrictionError2)
        fit.items.remove(holder1)
        fit.items.remove(holder2)
        self.assertBuffersEmpty(fit)

    def testPassHolderNoneGroup(self):
        # Check that holders with None group are not affected
        fit = Fit()
        holder1 = ShipItem(Type(None, groupId=None, attributes={Attribute.maxGroupOnline: 1}))
        holder1.state = State.online
        fit.items.append(holder1)
        holder2 = ShipItem(Type(None, groupId=None, attributes={Attribute.maxGroupOnline: 1}))
        holder2.state = State.online
        fit.items.append(holder2)
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.maxGroupOnline)
        self.assertIsNone(restrictionError1)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.maxGroupOnline)
        self.assertIsNone(restrictionError2)
        fit.items.remove(holder1)
        fit.items.remove(holder2)
        self.assertBuffersEmpty(fit)

    def testPassRestrictionNoneGroup(self):
        # None value doesn't restrict anything
        fit = Fit()
        holder1 = ShipItem(Type(None, groupId=1093, attributes={Attribute.maxGroupOnline: None}))
        holder1.state = State.online
        fit.items.append(holder1)
        holder2 = ShipItem(Type(None, groupId=1093, attributes={Attribute.maxGroupOnline: None}))
        holder2.state = State.online
        fit.items.append(holder2)
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.maxGroupOnline)
        self.assertIsNone(restrictionError1)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.maxGroupOnline)
        self.assertIsNone(restrictionError2)
        fit.items.remove(holder1)
        fit.items.remove(holder2)
        self.assertBuffersEmpty(fit)

    def testPassState(self):
        # No errors should occur if holders are not online+
        fit = Fit()
        holder1 = ShipItem(Type(None, groupId=886, attributes={Attribute.maxGroupOnline: 1}))
        fit.items.append(holder1)
        holder2 = ShipItem(Type(None, groupId=886, attributes={Attribute.maxGroupOnline: 1}))
        fit.items.append(holder2)
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.maxGroupOnline)
        self.assertIsNone(restrictionError1)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.maxGroupOnline)
        self.assertIsNone(restrictionError2)
        fit.items.remove(holder1)
        fit.items.remove(holder2)
        self.assertBuffersEmpty(fit)

    def testPassHolderNonShip(self):
        # Non-ship holders shouldn't be affected
        fit = Fit()
        holder1 = IndependentItem(Type(None, groupId=12, attributes={Attribute.maxGroupActive: 1}))
        holder1.state = State.online
        fit.items.append(holder1)
        holder2 = IndependentItem(Type(None, groupId=12, attributes={Attribute.maxGroupActive: 1}))
        holder2.state = State.online
        fit.items.append(holder2)
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.maxGroupActive)
        self.assertIsNone(restrictionError1)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.maxGroupActive)
        self.assertIsNone(restrictionError2)
        fit.items.remove(holder1)
        fit.items.remove(holder2)
        self.assertBuffersEmpty(fit)
