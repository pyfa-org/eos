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


from collections import namedtuple

from eos.const import Restriction
from eos.fit.restrictionTracker.exception import RegisterValidationError
from eos.fit.restrictionTracker.register import RestrictionRegister
from eos.util.keyedSet import KeyedSet


SkillUniquenessErrorData = namedtuple("SkillUniquenessErrorData", ("skill",))


class SkillUniquenessRegister(RestrictionRegister):
    """
    Implements restriction:
    Fit can't have more than one skill based on the same type.

    Details:
    Only holders having level attribute and item typeID other
    than None are tracked.
    """

    def __init__(self):
        # Container for skill holders
        # Format: {holder id: {holders}}
        self.__skillHolders = KeyedSet()

    def registerHolder(self, holder):
        # Only holders which have level attribute are tracked as skills
        if hasattr(holder, "level") is True and holder.item.id is not None:
            self.__skillHolders.addData(holder.item.id, holder)

    def unregisterHolder(self, holder):
        self.__skillHolders.rmData(holder.item.id, holder)

    def validate(self):
        taintedHolders = {}
        # Go through all skill IDs
        for skillId in self.__skillHolders:
            skillHolders = self.__skillHolders[skillId]
            # If there's at least two skills with the same ID,
            # taint these holders
            if len(skillHolders) > 1:
                for holder in skillHolders:
                    taintedHolders[holder] = SkillUniquenessErrorData(skill=skillId)
        if taintedHolders:
            raise RegisterValidationError(taintedHolders)

    @property
    def restrictionType(self):
        return Restriction.skillUniqueness
