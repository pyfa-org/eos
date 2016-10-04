# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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


from unittest.mock import Mock

from eos.const.eos import Domain, Restriction, State
from eos.fit.holder.item import ModuleHigh, Skill
from tests.restriction_tracker.restriction_testcase import RestrictionTestCase


class TestSkillRequirement(RestrictionTestCase):
    """Check functionality of skill requirement restriction"""

    def test_fail_single(self):
        # Check that error is raised when skill requirement
        # is not met
        item = self.ch.type_(type_id=1)
        item.required_skills = {50: 3}
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.skill_requirement)
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error, ((50, None, 3),))
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_multiple(self):
        # Check that multiple errors are shown as iterable
        item = self.ch.type_(type_id=1)
        item.required_skills = {48: 1, 50: 5}
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        skill_item = self.ch.type_(type_id=50)
        skill_holder = Mock(state=State.offline, item=skill_item, _domain=Domain.character, spec_set=Skill(1))
        skill_holder.level = 2
        self.track_holder(skill_holder)
        self.fit.skills[50] = skill_holder
        restriction_error = self.get_restriction_error(holder, Restriction.skill_requirement)
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error, ((50, 2, 5), (48, None, 1)))
        self.untrack_holder(holder)
        self.untrack_holder(skill_holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_partial(self):
        # Make sure satisfied skill requirements are not shown
        # up in error
        item = self.ch.type_(type_id=1)
        item.required_skills = {48: 1, 50: 5}
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        skill_item = self.ch.type_(type_id=48)
        skill_holder = Mock(state=State.offline, item=skill_item, _domain=Domain.character, spec_set=Skill(1))
        skill_holder.level = 5
        self.track_holder(skill_holder)
        self.fit.skills[48] = skill_holder
        restriction_error = self.get_restriction_error(holder, Restriction.skill_requirement)
        self.assertIsNotNone(restriction_error)
        self.assertCountEqual(restriction_error, ((50, None, 5),))
        self.untrack_holder(holder)
        self.untrack_holder(skill_holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_satisfied(self):
        # Check that error isn't raised when all skill requirements
        # are met
        item = self.ch.type_(type_id=1)
        item.required_skills = {50: 3}
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        skill_item = self.ch.type_(type_id=50)
        skill_holder = Mock(state=State.offline, item=skill_item, _domain=Domain.character, spec_set=Skill(1))
        skill_holder.level = 3
        self.track_holder(skill_holder)
        self.fit.skills[50] = skill_holder
        restriction_error = self.get_restriction_error(holder, Restriction.skill_requirement)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.untrack_holder(skill_holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()
