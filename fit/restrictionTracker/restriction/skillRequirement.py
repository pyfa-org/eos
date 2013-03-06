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

from eos.const import Restriction
from eos.fit.restrictionTracker.exception import RegisterValidationError
from eos.fit.restrictionTracker.register import RestrictionRegister
from eos.util.keyedSet import KeyedSet


SkillRequirementErrorData = namedtuple('SkillRequirementErrorData', ('skill', 'level', 'requiredLevel'))


class SkillRequirementRegister(RestrictionRegister):
    """
    Implements restriction:
    To use holder, all its skill requirements must be met.

    Details:
    Only holders having level attribute are tracked.
    Original item attributes are taken to determine skill and
    skill level requirements.
    If corresponding skill is found, but its skill level is None,
    check for holder is failed.
    """

    __slots__ = ('__skillHolders', '__restrictedHolders')

    def __init__(self):
        # Container for skill holders, for ease of
        # access
        # Format: {holder id: {holders}}
        self.__skillHolders = KeyedSet()
        # Set with holders which have any skill requirements
        # Format: {holders}
        self.__restrictedHolders = set()

    def registerHolder(self, holder):
        # Only holders which belong to character and have
        # level attribute are tracked as skills
        if hasattr(holder, 'level') is True:
            self.__skillHolders.addData(holder.item.id, holder)
        # Holders which have any skill requirement are tracked
        if holder.item.requiredSkills:
            self.__restrictedHolders.add(holder)

    def unregisterHolder(self, holder):
        self.__skillHolders.rmData(holder.item.id, holder)
        self.__restrictedHolders.discard(holder)

    def validate(self):
        taintedHolders = {}
        # Go through restricted holders
        for holder in self.__restrictedHolders:
            # Container for skill requirement errors
            skillRequirementErrors = []
            # Check each skill requirement
            for requiredSkillId in holder.item.requiredSkills:
                requiredSkillLevel = holder.item.requiredSkills[requiredSkillId]
                skillHolders = self.__skillHolders.get(requiredSkillId) or ()
                # Pick max level of all skill holders, absence of skill
                # is considered as skill level set to None
                skillLevel = None
                for skillHolder in skillHolders:
                    skillHolderLevel = skillHolder.level
                    if skillLevel is None:
                        skillLevel = skillHolderLevel
                    elif skillHolderLevel is not None:
                        skillLevel = max(skillLevel, skillHolderLevel)
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
