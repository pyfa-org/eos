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
from eos.tests.restrictionTracker.environment import Fit, IndependentItem
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestSubsystemIndex(RestrictionTestCase):
    """Check functionality of subsystem slot index restriction"""

    def testFail(self):
        # Check that if 2 or more holders are put into single slot
        # index, error is raised
        fit = Fit()
        item = self.dh.type_(typeId=1, attributes={Attribute.subSystemSlot: 120})
        holder1 = IndependentItem(item)
        fit.items.append(holder1)
        holder2 = IndependentItem(item)
        fit.items.append(holder2)
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.subsystemIndex)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.holderSlotIndex, 120)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.subsystemIndex)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.holderSlotIndex, 120)
        fit.items.remove(holder1)
        fit.items.remove(holder2)
        self.assertBuffersEmpty(fit)

    def testFailOriginal(self):
        # Make sure that original attributes are used
        fit = Fit()
        item = self.dh.type_(typeId=1, attributes={Attribute.subSystemSlot: 120})
        holder1 = IndependentItem(item)
        holder1.attributes[Attribute.subSystemSlot] = 119
        fit.items.append(holder1)
        holder2 = IndependentItem(item)
        holder2.attributes[Attribute.subSystemSlot] = 121
        fit.items.append(holder2)
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.subsystemIndex)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.holderSlotIndex, 120)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.subsystemIndex)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.holderSlotIndex, 120)
        fit.items.remove(holder1)
        fit.items.remove(holder2)
        self.assertBuffersEmpty(fit)

    def testPass(self):
        # Single holder which takes some slot shouldn't
        # trigger any errors
        fit = Fit()
        holder = IndependentItem(self.dh.type_(typeId=1, attributes={Attribute.subSystemSlot: 120}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.subsystemIndex)
        self.assertIsNone(restrictionError)
        fit.items.remove(holder)
        self.assertBuffersEmpty(fit)

    def testPassDifferent(self):
        # Holders taking different slots shouldn't trigger any errors
        fit = Fit()
        holder1 = IndependentItem(self.dh.type_(typeId=1, attributes={Attribute.subSystemSlot: 120}))
        fit.items.append(holder1)
        holder2 = IndependentItem(self.dh.type_(typeId=2, attributes={Attribute.subSystemSlot: 121}))
        fit.items.append(holder2)
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.subsystemIndex)
        self.assertIsNone(restrictionError1)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.subsystemIndex)
        self.assertIsNone(restrictionError2)
        fit.items.remove(holder1)
        fit.items.remove(holder2)
        self.assertBuffersEmpty(fit)
