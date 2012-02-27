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
from eos.tests.restrictionTracker.environment import Fit, IndependentItem, Skill
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestSkillRequirement(RestrictionTestCase):
    """Check functionality of skill requirement restriction"""

    def testFailSingle1(self):
        # Check that error is raised when single skill requirement
        # is not met
        fit = Fit()
        holder = IndependentItem(Type(None, attributes={Attribute.requiredSkill1: 50, Attribute.requiredSkill1Level: 3}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.skillRequirement)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError, ((50, None, 3),))
        fit.items.remove(holder)
        self.assertBuffersEmpty(fit)

    def testFailSingle2(self):
        fit = Fit()
        holder = IndependentItem(Type(None, attributes={Attribute.requiredSkill2: 50, Attribute.requiredSkill2Level: 3}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.skillRequirement)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError, ((50, None, 3),))
        fit.items.remove(holder)
        self.assertBuffersEmpty(fit)

    def testFailSingle3(self):
        fit = Fit()
        holder = IndependentItem(Type(None, attributes={Attribute.requiredSkill3: 50, Attribute.requiredSkill3Level: 3}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.skillRequirement)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError, ((50, None, 3),))
        fit.items.remove(holder)
        self.assertBuffersEmpty(fit)

    def testFailSingle4(self):
        fit = Fit()
        holder = IndependentItem(Type(None, attributes={Attribute.requiredSkill4: 50, Attribute.requiredSkill4Level: 3}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.skillRequirement)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError, ((50, None, 3),))
        fit.items.remove(holder)
        self.assertBuffersEmpty(fit)

    def testFailSingle5(self):
        fit = Fit()
        holder = IndependentItem(Type(None, attributes={Attribute.requiredSkill5: 50, Attribute.requiredSkill5Level: 3}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.skillRequirement)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError, ((50, None, 3),))
        fit.items.remove(holder)
        self.assertBuffersEmpty(fit)

    def testFailSingle6(self):
        fit = Fit()
        holder = IndependentItem(Type(None, attributes={Attribute.requiredSkill6: 50, Attribute.requiredSkill6Level: 3}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.skillRequirement)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError, ((50, None, 3),))
        fit.items.remove(holder)
        self.assertBuffersEmpty(fit)

    def testFailMultiple(self):
        # Check error raised when multiple skill requirements
        # are not met
        fit = Fit()
        holder = IndependentItem(Type(None, attributes={Attribute.requiredSkill1: 50, Attribute.requiredSkill1Level: 5,
                                                        Attribute.requiredSkill2: 48, Attribute.requiredSkill2Level: 1}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.skillRequirement)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError, ((50, None, 5), (48, None, 1)))
        fit.items.remove(holder)
        self.assertBuffersEmpty(fit)

    def testFailPartial(self):
        # Make sure satisfied skill requirements are not shown
        # up in error
        fit = Fit()
        holder = IndependentItem(Type(None, attributes={Attribute.requiredSkill1: 50, Attribute.requiredSkill1Level: 5,
                                                        Attribute.requiredSkill2: 48, Attribute.requiredSkill2Level: 1}))
        fit.items.append(holder)
        skill = Skill(Type(48))
        skill.level = 5
        fit.items.append(skill)
        restrictionError = fit.getRestrictionError(holder, Restriction.skillRequirement)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError, ((50, None, 5),))
        fit.items.remove(holder)
        fit.items.remove(skill)
        self.assertBuffersEmpty(fit)

    def testFailOriginal(self):
        # make sure original attributes are used
        fit = Fit()
        holder = IndependentItem(Type(None, attributes={Attribute.requiredSkill1: 50, Attribute.requiredSkill1Level: 3}))
        holder.attributes[Attribute.requiredSkill1] = 47
        holder.attributes[Attribute.requiredSkill1Level] = 1
        fit.items.append(holder)
        skill = Skill(Type(47))
        skill.level = 1
        fit.items.append(skill)
        restrictionError = fit.getRestrictionError(holder, Restriction.skillRequirement)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError, ((50, None, 3),))
        fit.items.remove(holder)
        fit.items.remove(skill)
        self.assertBuffersEmpty(fit)

    def testPassSatisfied(self):
        # Check that error isn't raised when all skill requirements
        # are met
        fit = Fit()
        holder = IndependentItem(Type(None, attributes={Attribute.requiredSkill1: 50, Attribute.requiredSkill1Level: 3}))
        fit.items.append(holder)
        skill = Skill(Type(50))
        skill.level = 3
        fit.items.append(skill)
        restrictionError = fit.getRestrictionError(holder, Restriction.skillRequirement)
        self.assertIsNone(restrictionError)
        fit.items.remove(holder)
        fit.items.remove(skill)
        self.assertBuffersEmpty(fit)

    def testPassMultiSkill(self):
        # Make sure max skill level is taken
        fit = Fit()
        holder = IndependentItem(Type(None, attributes={Attribute.requiredSkill1: 50, Attribute.requiredSkill1Level: 4}))
        fit.items.append(holder)
        skill1 = Skill(Type(50))
        skill1.level = 1
        fit.items.append(skill1)
        skill2 = Skill(Type(50))
        skill2.level = 5
        fit.items.append(skill2)
        restrictionError = fit.getRestrictionError(holder, Restriction.skillRequirement)
        self.assertIsNone(restrictionError)
        fit.items.remove(holder)
        fit.items.remove(skill1)
        fit.items.remove(skill2)

    def testPassMultiSkillNone(self):
        # Make sure that None-leveled skills are overridden
        fit = Fit()
        holder = IndependentItem(Type(None, attributes={Attribute.requiredSkill1: 50, Attribute.requiredSkill1Level: 0}))
        fit.items.append(holder)
        skill1 = Skill(Type(50))
        skill1.level = None
        fit.items.append(skill1)
        skill2 = Skill(Type(50))
        skill2.level = 0
        fit.items.append(skill2)
        restrictionError = fit.getRestrictionError(holder, Restriction.skillRequirement)
        self.assertIsNone(restrictionError)
        fit.items.remove(holder)
        fit.items.remove(skill1)
        fit.items.remove(skill2)
        self.assertBuffersEmpty(fit)

    def testPassNoneSkill(self):
        # When skill requirement ID is None, no actual
        # skill requirements should be generated
        fit = Fit()
        holder = IndependentItem(Type(None, attributes={Attribute.requiredSkill1: None, Attribute.requiredSkill1Level: 5}))
        fit.items.append(holder)
        restrictionError = fit.getRestrictionError(holder, Restriction.skillRequirement)
        self.assertIsNone(restrictionError)
        fit.items.remove(holder)
        self.assertBuffersEmpty(fit)
