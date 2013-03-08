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
from eos.tests.restrictionTracker.environment import Fit, IndependentItem, Skill
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestSkillRequirement(RestrictionTestCase):
    """Check functionality of skill requirement restriction"""

    def testFailSingle(self):
        # Check that error is raised when single skill requirement
        # is not met
        fit = Fit()
        item = self.ch.type_(typeId=1)
        item.requiredSkills = {50: 3}
        holder = IndependentItem(item)
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.skillRequirement)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError, ((50, None, 3),))
        fit.items.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(fit)

    def testFailMultiple(self):
        # Check error raised when multiple skill requirements
        # are not met
        fit = Fit()
        item = self.ch.type_(typeId=1)
        item.requiredSkills = {48: 1, 50: 5}
        holder = IndependentItem(item)
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.skillRequirement)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError, ((50, None, 5), (48, None, 1)))
        fit.items.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(fit)

    def testFailPartial(self):
        # Make sure satisfied skill requirements are not shown
        # up in error
        fit = Fit()
        item = self.ch.type_(typeId=1)
        item.requiredSkills = {48: 1, 50: 5}
        holder = IndependentItem(item)
        fit.items.append(holder)
        skill = Skill(self.ch.type_(typeId=48))
        skill.level = 5
        fit.items.append(skill)
        restrictionError = fit.getRestrictionError(holder, Restriction.skillRequirement)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError, ((50, None, 5),))
        fit.items.remove(holder)
        fit.items.remove(skill)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(fit)

    def testPassSatisfied(self):
        # Check that error isn't raised when all skill requirements
        # are met
        fit = Fit()
        item = self.ch.type_(typeId=1)
        item.requiredSkills = {50: 3}
        holder = IndependentItem(item)
        fit.items.append(holder)
        skill = Skill(self.ch.type_(typeId=50))
        skill.level = 3
        fit.items.append(skill)
        restrictionError = fit.getRestrictionError(holder, Restriction.skillRequirement)
        self.assertIsNone(restrictionError)
        fit.items.remove(holder)
        fit.items.remove(skill)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(fit)

    def testPassMultiSkill(self):
        # Make sure max skill level is taken
        fit = Fit()
        item1 = self.ch.type_(typeId=1)
        item1.requiredSkills = {50: 4}
        holder = IndependentItem(item1)
        fit.items.append(holder)
        item2 = self.ch.type_(typeId=50)
        skill1 = Skill(item2)
        skill1.level = 1
        fit.items.append(skill1)
        skill2 = Skill(item2)
        skill2.level = 5
        fit.items.append(skill2)
        restrictionError = fit.getRestrictionError(holder, Restriction.skillRequirement)
        self.assertIsNone(restrictionError)
        fit.items.remove(holder)
        fit.items.remove(skill1)
        fit.items.remove(skill2)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(fit)

    def testPassMultiSkillNone(self):
        # Make sure that None-leveled skills are overridden
        # by skills which have some skill level
        fit = Fit()
        item1 = self.ch.type_(typeId=1)
        item1.requiredSkills = {50: 0}
        holder = IndependentItem(item1)
        fit.items.append(holder)
        item2 = self.ch.type_(typeId=50)
        skill1 = Skill(item2)
        skill1.level = None
        fit.items.append(skill1)
        skill2 = Skill(item2)
        skill2.level = 0
        fit.items.append(skill2)
        restrictionError = fit.getRestrictionError(holder, Restriction.skillRequirement)
        self.assertIsNone(restrictionError)
        fit.items.remove(holder)
        fit.items.remove(skill1)
        fit.items.remove(skill2)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(fit)
