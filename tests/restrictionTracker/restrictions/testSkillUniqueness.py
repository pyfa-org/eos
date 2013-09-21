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
from eos.fit.holder.item import Implant, Skill
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestSkillUniqueness(RestrictionTestCase):
    """Check functionality of skill uniqueness restriction"""

    def testFail(self):
        # Check that multiple skills with this ID raise error
        item = self.ch.type_(typeId=56)
        skill1 = Mock(state=State.offline, item=item, level=1, _location=Location.character, spec_set=Skill)
        skill2 = Mock(state=State.offline, item=item, level=2, _location=Location.character, spec_set=Skill)
        self.trackHolder(skill1)
        self.trackHolder(skill2)
        restrictionError1 = self.getRestrictionError(skill1, Restriction.skillUniqueness)
        self.assertIsNotNone(restrictionError1)
        self.assertEqual(restrictionError1.skill, 56)
        restrictionError2 = self.getRestrictionError(skill2, Restriction.skillUniqueness)
        self.assertIsNotNone(restrictionError2)
        self.assertEqual(restrictionError2.skill, 56)
        self.untrackHolder(skill1)
        self.untrackHolder(skill2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPass(self):
        # No error should be raised when single skill
        # is added to fit
        item = self.ch.type_(typeId=56)
        skill = Mock(state=State.offline, item=item, level=1, _location=Location.character, spec_set=Skill)
        self.trackHolder(skill)
        restrictionError = self.getRestrictionError(skill, Restriction.skillUniqueness)
        self.assertIsNone(restrictionError)
        self.untrackHolder(skill)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassNone(self):
        # When typeIDs of skills are None, they should be ignored
        item = self.ch.type_(typeId=None)
        skill1 = Mock(state=State.offline, item=item, level=1, _location=Location.character, spec_set=Skill)
        skill2 = Mock(state=State.offline, item=item, level=2, _location=Location.character, spec_set=Skill)
        self.trackHolder(skill1)
        self.trackHolder(skill2)
        restrictionError1 = self.getRestrictionError(skill1, Restriction.skillUniqueness)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(skill2, Restriction.skillUniqueness)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(skill1)
        self.untrackHolder(skill2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testPassNonSkills(self):
        # Not-skill holders shouldn't be tracked
        item = self.ch.type_(typeId=56)
        skill1 = Mock(state=State.offline, item=item, _location=Location.character, spec_set=Implant)
        skill2 = Mock(state=State.offline, item=item, _location=Location.character, spec_set=Implant)
        self.trackHolder(skill1)
        self.trackHolder(skill2)
        restrictionError1 = self.getRestrictionError(skill1, Restriction.skillUniqueness)
        self.assertIsNone(restrictionError1)
        restrictionError2 = self.getRestrictionError(skill2, Restriction.skillUniqueness)
        self.assertIsNone(restrictionError2)
        self.untrackHolder(skill1)
        self.untrackHolder(skill2)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()
