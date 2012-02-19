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


from eos.const import Location
from eos.fit.restrictionTracker.exception import SkillRequirementException
from eos.fit.restrictionTracker.register import RestrictionRegister


class SkillRequirementRegister(RestrictionRegister):
    """
    Implements restriction:
    To use holder, all its skill requirements must be met.

    Details:
    Original item attributes are taken to determine skill and
    skill level requirements.
    If required skill level is None, skill requirement check
    is skipped.
    If corresponding skill is found, but its skill level is None,
    check for holder is failed.
    """

    def __init__(self):
        # Container for skill holders, for ease of
        # access
        # Format: {holder id: holder}
        self.__skillHolders = {}
        # Set with holders which have any skill requirements
        # Format: {holders}
        self.__restrictedHolders = set()

    def registerHolder(self, holder):
        # Only holders which belong to character and have
        # level attribute are tracked as skills
        if holder._location == Location.character and hasattr(holder, "level") is True:
            self.__skillHolders[holder.item.id] = holder
        # Holders which have any skill requirement are tracked
        if len(holder.item.requiredSkills) > 0:
            self.__restrictedHolders.add(holder)

    def unregisterHolder(self, holder):
        try:
            self.__skillHolders[holder.item.id]
        except KeyError:
            pass
        self.__restrictedHolders.discard(holder)

    def validate(self):
        taintedHolders = set()
        # Go through restricted holders
        for restrictedHolder in self.__restrictedHolders:
            # Check each skill requirement
            for requiredSkillId in restrictedHolder.item.requiredSkills:
                requiredSkillLevel = restrictedHolder.item.requiredSkills[requiredSkillId]
                # If required skill level is None, skip it
                if requiredSkillLevel is None:
                    continue
                # If skill is required at some level, but we don't have corresponding
                # skill holder in skill container - mark holder as tainted and move to
                # checking next one
                skillHolder = self.__skillHolders.get(requiredSkillId)
                if skillHolder is None:
                    taintedHolders.add(restrictedHolder)
                    break
                # Last check - if skill level is lower than expected, current holder
                # is tainted; mark it so and move to the next one
                skillLevel = skillHolder.level
                if skillLevel is None or skillLevel < requiredSkillLevel:
                    taintedHolders.add(restrictedHolder)
                    break
        if len(taintedHolders) > 0:
            raise SkillRequirementException(taintedHolders)
