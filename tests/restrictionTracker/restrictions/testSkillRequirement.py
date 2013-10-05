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


from unittest.mock import Mock

from eos.const.eos import Location, Restriction, State
from eos.fit.holder.item import Module, Skill
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestSkillRequirement(RestrictionTestCase):
    """Check functionality of skill requirement restriction"""

    def testFailSingle(self):
        # Check that error is raised when skill requirement
        # is not met
        item = self.ch.type_(typeId=1)
        item.requiredSkills = {50: 3}
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.skillRequirement)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError, ((50, None, 3),))
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailMultiple(self):
        # Check that multiple errors are shown as iterable
        item = self.ch.type_(typeId=1)
        item.requiredSkills = {48: 1, 50: 5}
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        skillItem = self.ch.type_(typeId=50)
        skillHolder = Mock(state=State.offline, item=skillItem, _location=Location.character, spec_set=Skill)
        skillHolder.level = 2
        self.trackHolder(skillHolder)
        self.fit.skills[50] = skillHolder
        restrictionError = self.getRestrictionError(holder, Restriction.skillRequirement)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError, ((50, 2, 5), (48, None, 1)))
        self.untrackHolder(holder)
        self.untrackHolder(skillHolder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testFailPartial(self):
        # Make sure satisfied skill requirements are not shown
        # up in error
        item = self.ch.type_(typeId=1)
        item.requiredSkills = {48: 1, 50: 5}
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        skillItem = self.ch.type_(typeId=48)
        skillHolder = Mock(state=State.offline, item=skillItem, _location=Location.character, spec_set=Skill)
        skillHolder.level = 5
        self.trackHolder(skillHolder)
        self.fit.skills[48] = skillHolder
        restrictionError = self.getRestrictionError(holder, Restriction.skillRequirement)
        self.assertIsNotNone(restrictionError)
        self.assertCountEqual(restrictionError, ((50, None, 5),))
        self.untrackHolder(holder)
        self.untrackHolder(skillHolder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassSatisfied(self):
        # Check that error isn't raised when all skill requirements
        # are met
        item = self.ch.type_(typeId=1)
        item.requiredSkills = {50: 3}
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        skillItem = self.ch.type_(typeId=50)
        skillHolder = Mock(state=State.offline, item=skillItem, _location=Location.character, spec_set=Skill)
        skillHolder.level = 3
        self.trackHolder(skillHolder)
        self.fit.skills[50] = skillHolder
        restrictionError = self.getRestrictionError(holder, Restriction.skillRequirement)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.untrackHolder(skillHolder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()
