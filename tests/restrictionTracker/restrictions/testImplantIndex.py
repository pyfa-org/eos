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


from eos.const.eos import Restriction
from eos.const.eve import Attribute
from eos.tests.restrictionTracker.environment import Fit, IndependentItem
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestImplantIndex(RestrictionTestCase):
    """Check functionality of implant slot index restriction"""

    def testFail(self):
        # Check that if 2 or more holders are put into single slot
        # index, error is raised
        fit = Fit()
        item = self.ch.type_(typeId=1, attributes={Attribute.implantness: 120})
        holder1 = IndependentItem(item)
        fit.items.append(holder1)
        holder2 = IndependentItem(item)
        fit.items.append(holder2)
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.implantIndex)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.holderSlotIndex, 120)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.implantIndex)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.holderSlotIndex, 120)
        fit.items.remove(holder1)
        fit.items.remove(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(fit)

    def testFailOriginal(self):
        # Make sure that original attributes are used
        fit = Fit()
        item = self.ch.type_(typeId=1, attributes={Attribute.implantness: 120})
        holder1 = IndependentItem(item)
        holder1.attributes[Attribute.implantness] = 119
        fit.items.append(holder1)
        holder2 = IndependentItem(item)
        holder2.attributes[Attribute.implantness] = 121
        fit.items.append(holder2)
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.implantIndex)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.holderSlotIndex, 120)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.implantIndex)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.holderSlotIndex, 120)
        fit.items.remove(holder1)
        fit.items.remove(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(fit)

    def testPass(self):
        # Single holder which takes some slot shouldn't
        # trigger any errors
        fit = Fit()
        holder = IndependentItem(self.ch.type_(typeId=1, attributes={Attribute.implantness: 120}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.implantIndex)
        self.assertIsNone(restrictionError)
        fit.items.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(fit)

    def testPassDifferent(self):
        # Holders taking different slots shouldn't trigger any errors
        fit = Fit()
        holder1 = IndependentItem(self.ch.type_(typeId=1, attributes={Attribute.implantness: 120}))
        fit.items.append(holder1)
        holder2 = IndependentItem(self.ch.type_(typeId=2, attributes={Attribute.implantness: 121}))
        fit.items.append(holder2)
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.implantIndex)
        self.assertIsNone(restrictionError1)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.implantIndex)
        self.assertIsNone(restrictionError2)
        fit.items.remove(holder1)
        fit.items.remove(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(fit)
