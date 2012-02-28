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
from eos.eve.type import Type
from eos.tests.restrictionTracker.environment import Fit, IndependentItem, Skill
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestSkillUniqueness(RestrictionTestCase):
    """Check functionality of skill uniqueness restriction"""

    def testFail(self):
        # Check that multiple skills with this ID raise error
        fit = Fit()
        skill1 = Skill(Type(56))
        fit.items.append(skill1)
        skill2 = Skill(Type(56))
        fit.items.append(skill2)
        restrictionError1 = fit.getRestrictionError(skill1, Restriction.skillUniqueness)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.skill, 56)
        restrictionError2 = fit.getRestrictionError(skill1, Restriction.skillUniqueness)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.skill, 56)
        fit.items.remove(skill1)
        fit.items.remove(skill2)
        self.assertBuffersEmpty(fit)

    def testPass(self):
        # No error should be raised when single skill
        # is added to fit
        fit = Fit()
        skill = Skill(Type(56))
        fit.items.append(skill)
        restrictionError = fit.getRestrictionError(skill, Restriction.skillUniqueness)
        self.assertIsNone(restrictionError)
        fit.items.remove(skill)
        self.assertBuffersEmpty(fit)

    def testPassNone(self):
        # When typeIDs of skills are None, they should be ignored
        fit = Fit()
        skill1 = Skill(Type(None))
        fit.items.append(skill1)
        skill2 = Skill(Type(None))
        fit.items.append(skill2)
        restrictionError1 = fit.getRestrictionError(skill1, Restriction.skillUniqueness)
        self.assertIsNone(restrictionError1)
        restrictionError2 = fit.getRestrictionError(skill2, Restriction.skillUniqueness)
        self.assertIsNone(restrictionError2)
        fit.items.remove(skill1)
        fit.items.remove(skill2)
        self.assertBuffersEmpty(fit)

    def testPassNonSkills(self):
        # Not-skill holders shouldn't be tracked
        fit = Fit()
        holder1 = IndependentItem(Type(70))
        fit.items.append(holder1)
        holder2 = IndependentItem(Type(70))
        fit.items.append(holder2)
        restrictionError1 = fit.getRestrictionError(holder1, Restriction.skillUniqueness)
        self.assertIsNone(restrictionError1)
        restrictionError2 = fit.getRestrictionError(holder2, Restriction.skillUniqueness)
        self.assertIsNone(restrictionError2)
        fit.items.remove(holder1)
        fit.items.remove(holder2)
        self.assertBuffersEmpty(fit)
