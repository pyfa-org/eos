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


from collections import namedtuple

from eos.const.eos import Restriction
from eos.fit.item import Rig
from .base import BaseRestrictionRegister
from ..exception import RegisterValidationError


SkillRequirementErrorData = namedtuple('SkillRequirementErrorData', ('skill', 'level', 'required_level'))

EXCEPTIONS = (Rig,)


class SkillRequirementRestrictionRegister(BaseRestrictionRegister):
    """
    Implements restriction:
    To use item, all its skill requirements must be met.

    Details:
    Only items located within fit.skills container are able to
        satisfy skill requirements.
    EVE type attributes are taken to determine skill and skill
        level requirements.
    If corresponding skill is found, but its skill level is None,
        check for item is failed.
    """

    def __init__(self, fit):
        self._fit = fit
        # Set with items which have any skill requirements
        # Format: {items}
        self.__restricted_items = set()

    def register_item(self, holder):
        # Holders which are not exceptions and which have any
        # skill requirement are tracked
        if holder._eve_type.required_skills and not isinstance(holder, EXCEPTIONS):
            self.__restricted_items.add(holder)

    def unregister_item(self, holder):
        self.__restricted_items.discard(holder)

    def validate(self):
        tainted_holders = {}
        # Go through restricted holders
        for holder in self.__restricted_items:
            # Container for skill requirement errors
            # for current holder
            skill_requirement_errors = []
            # Check each skill requirement
            for required_skill_id in holder._eve_type.required_skills:
                required_skill_level = holder._eve_type.required_skills[required_skill_id]
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
