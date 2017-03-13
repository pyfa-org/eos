# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2017 Anton Vorobyov
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
# ===============================================================================


from eos import *
from eos.const.eos import Restriction, State
from tests.integration.restriction.restriction_testcase import RestrictionTestCase


class TestSkillRequirement(RestrictionTestCase):
    """Check functionality of skill requirement restriction"""

    def test_fail_single(self):
        # Check that error is raised when skill requirement
        # is not met
        fit = Fit()
        eve_type = self.ch.type()
        eve_type.required_skills = {50: 3}
        item = ModuleHigh(eve_type.id, state=State.offline)
        self.add_item(item)
        restriction_error = self.get_restriction_error(fit, item, Restriction.skill_requirement)
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error, ((50, None, 3),))
        self.remove_item(item)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_fail_multiple(self):
        # Check that multiple errors are shown as iterable
        fit = Fit()
        eve_type = self.ch.type()
        eve_type.required_skills = {48: 1, 50: 5}
        item = ModuleHigh(eve_type.id, state=State.offline)
        self.add_item(item)
        skill_eve_type = self.ch.type()
        skill_item = Skill(skill_eve_type.id)
        skill_item.level = 2
        self.add_item(skill_item)
        fit.skills[50] = skill_item
        restriction_error = self.get_restriction_error(fit, item, Restriction.skill_requirement)
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error, ((50, 2, 5), (48, None, 1)))
        self.remove_item(item)
        self.remove_item(skill_item)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_fail_partial(self):
        # Make sure satisfied skill requirements are not shown
        # up in error
        fit = Fit()
        eve_type = self.ch.type()
        eve_type.required_skills = {48: 1, 50: 5}
        item = ModuleHigh(eve_type.id, state=State.offline)
        self.add_item(item)
        skill_eve_type = self.ch.type()
        skill_item = Skill(skill_eve_type.id)
        skill_item.level = 5
        self.add_item(skill_item)
        fit.skills[48] = skill_item
        restriction_error = self.get_restriction_error(fit, item, Restriction.skill_requirement)
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error, ((50, None, 5),))
        self.remove_item(item)
        self.remove_item(skill_item)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_satisfied(self):
        # Check that error isn't raised when all skill requirements
        # are met
        fit = Fit()
        eve_type = self.ch.type()
        eve_type.required_skills = {50: 3}
        item = ModuleHigh(eve_type.id, state=State.offline)
        self.add_item(item)
        skill_eve_type = self.ch.type()
        skill_item = Skill(skill_eve_type.id)
        skill_item.level = 3
        self.add_item(skill_item)
        fit.skills[50] = skill_item
        restriction_error = self.get_restriction_error(fit, item, Restriction.skill_requirement)
        self.assertIsNone(restriction_error)
        self.remove_item(item)
        self.remove_item(skill_item)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_exception_rig(self):
        # Check that skillreqs on rigs are not checked
        fit = Fit()
        eve_type = self.ch.type()
        eve_type.required_skills = {50: 3}
        item = Rig(eve_type.id)
        self.add_item(item)
        restriction_error = self.get_restriction_error(fit, item, Restriction.skill_requirement)
        self.assertIsNone(restriction_error)
        self.remove_item(item)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
