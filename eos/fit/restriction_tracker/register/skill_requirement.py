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


from collections import namedtuple

from eos.const.eos import Restriction
from eos.fit.restriction_tracker.exception import RegisterValidationError
from .abc import RestrictionRegister


SkillRequirementErrorData = namedtuple('SkillRequirementErrorData', ('skill', 'level', 'required_level'))


class SkillRequirementRegister(RestrictionRegister):
    """
    Implements restriction:
    To use holder, all its skill requirements must be met.

    Details:
    Only holders located within fit.skills container are able to
    satisfy skill requirements.
    Original item attributes are taken to determine skill and
    skill level requirements.
    If corresponding skill is found, but its skill level is None,
    check for holder is failed.
    """

    def __init__(self, fit):
        self._fit = fit
        # Set with holders which have any skill requirements
        # Format: {holders}
        self.__restricted_holders = set()

    def register_holder(self, holder):
        # Holders which have any skill requirement are tracked
        if holder.item.required_skills:
            self.__restricted_holders.add(holder)

    def unregister_holder(self, holder):
        self.__restricted_holders.discard(holder)

    def validate(self):
        tainted_holders = {}
        # Go through restricted holders
        for holder in self.__restricted_holders:
            # Container for skill requirement errors
            # for current holder
            skill_requirement_errors = []
            # Check each skill requirement
            for required_skill_id in holder.item.required_skills:
                required_skill_level = holder.item.required_skills[required_skill_id]
                # Get skill level with None as fallback value for case
                # when we don't have such skill in fit
                try:
                    skill_level = self._fit.skills[required_skill_id].level
                except KeyError:
                    skill_level = None
                # Last check - if skill level is lower than expected, current holder
                # is tainted; mark it so and move to the next one
                if skill_level is None or skill_level < required_skill_level:
                    skill_requirement_error = SkillRequirementErrorData(
                        skill=required_skill_id,
                        level=skill_level,
                        required_level=required_skill_level
                    )
                    skill_requirement_errors.append(skill_requirement_error)
            if skill_requirement_errors:
                tainted_holders[holder] = tuple(skill_requirement_errors)
        if tainted_holders:
            raise RegisterValidationError(tainted_holders)

    @property
    def restriction_type(self):
        return Restriction.skill_requirement
