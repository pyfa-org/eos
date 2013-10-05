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


from collections import namedtuple

from eos.const.eos import Restriction
from eos.fit.restrictionTracker.exception import RegisterValidationError
from .abc import RestrictionRegister


SkillRequirementErrorData = namedtuple('SkillRequirementErrorData', ('skill', 'level', 'requiredLevel'))


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
        self.__restrictedHolders = set()

    def registerHolder(self, holder):
        # Holders which have any skill requirement are tracked
        if holder.item.requiredSkills:
            self.__restrictedHolders.add(holder)

    def unregisterHolder(self, holder):
        self.__restrictedHolders.discard(holder)

    def validate(self):
        taintedHolders = {}
        # Go through restricted holders
        for holder in self.__restrictedHolders:
            # Container for skill requirement errors
            # for current holder
            skillRequirementErrors = []
            # Check each skill requirement
            for requiredSkillId in holder.item.requiredSkills:
                requiredSkillLevel = holder.item.requiredSkills[requiredSkillId]
                # Get skill level with None as fallback value for case
                # when we don't have such skill in fit
                try:
                    skillLevel = self._fit.skills[requiredSkillId].level
                except KeyError:
                    skillLevel = None
                # Last check - if skill level is lower than expected, current holder
                # is tainted; mark it so and move to the next one
                if skillLevel is None or skillLevel < requiredSkillLevel:
                    skillRequirementError = SkillRequirementErrorData(skill=requiredSkillId,
                                                                      level=skillLevel,
                                                                      requiredLevel=requiredSkillLevel)
                    skillRequirementErrors.append(skillRequirementError)
            if skillRequirementErrors:
                taintedHolders[holder] = tuple(skillRequirementErrors)
        if taintedHolders:
            raise RegisterValidationError(taintedHolders)

    @property
    def restrictionType(self):
        return Restriction.skillRequirement
