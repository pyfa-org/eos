#===============================================================================
# Copyright (C) 2011 Diego Duclos
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

from eos import const
from .localData import durationMods, mirrorDurationMods
from ..info import EffectInfo

# Values which are considered as 'empty' values
nulls = {0, None}

class Modifier:
    """
    Internal builder object, stores meaningful elements of expression tree temporarily
    and provides facilities to convert them to ExpressionInfo objects
    """
    def __init__(self):
        # Conditions under which modification can be applied
        self.conditions = None
        # Type of modification
        self.type = None
        # Source attribute ID
        self.sourceAttribute = None
        # Operation to be applied on target
        self.operation = None
        # Target attribute ID
        self.targetAttribute = None
        # Target location for modification
        self.targetLocation = None
        # Target group ID of items
        self.targetGroup = None
        # Skill requirement ID of target items
        self.targetSkillRq = None
        # For instant effects, describes when it should be applied
        self.runTime = None

    # Set of validation methods
    def validate(self):
        """Self-validation for modifier objects"""
        # These fields always should be filled
        if self.targetAttribute in nulls or self.sourceAttribute in nulls:
            return False
        # Check condition tree
        if self.conditions is not None:
            if self.conditions.validateTree() is not True:
                return False
        # Other fields are optional, check them using modifier type
        validateMap = {const.opndAddGangGrpMod: self.__valGangGrp,
                       const.opndRmGangGrpMod: self.__valGangGrp,
                       const.opndAddGangItmMod: self.__valGangItm,
                       const.opndRmGangItmMod: self.__valGangItm,
                       const.opndAddGangOwnSrqMod: self.__valGangOwnSrq,
                       const.opndRmGangOwnSrqMod: self.__valGangOwnSrq,
                       const.opndAddGangSrqMod: self.__valGangSrq,
                       const.opndRmGangSrqMod: self.__valGangSrq,
                       const.opndAddItmMod: self.__valItm,
                       const.opndRmItmMod: self.__valItm,
                       const.opndAddLocGrpMod: self.__valLocGrp,
                       const.opndRmLocGrpMod: self.__valLocGrp,
                       const.opndAddLocMod: self.__valLoc,
                       const.opndRmLocMod: self.__valLoc,
                       const.opndAddLocSrqMod: self.__valLocSrq,
                       const.opndRmLocSrqMod: self.__valLocSrq,
                       const.opndAddOwnSrqMod: self.__valOwnSrq,
                       const.opndRmOwnSrqMod: self.__valOwnSrq,
                       const.opndAssign: self.__valInstant,
                       const.opndInc: self.__valInstant,
                       const.opndDec: self.__valInstant}
        try:
            method = validateMap[self.type]
        except KeyError:
            return False
        return method()

    def __valGangGrp(self):
        if self.targetLocation is not None or self.targetSkillRq is not None or \
        self.runTime is not None:
            return False
        if self.operation in nulls or self.targetGroup in nulls:
            return False
        return True

    def __valGangItm(self):
        if self.targetGroup is not None or self.targetSkillRq is not None or \
        self.targetLocation is not None or self.runTime is not None:
            return False
        if self.operation in nulls:
            return False
        return True

    def __valGangOwnSrq(self):
        if self.targetLocation is not None or self.targetGroup is not None or \
        self.runTime is not None:
            return False
        if self.operation in nulls or self.targetSkillRq in nulls:
            return False
        return True

    def __valGangSrq(self):
        if self.targetLocation is not None or self.targetGroup is not None or \
        self.runTime is not None:
            return False
        if self.operation in nulls or self.targetSkillRq in nulls:
            return False
        return True

    def __valItm(self):
        if self.targetGroup is not None or self.targetSkillRq is not None or \
        self.runTime is not None:
            return False
        if self.operation in nulls or self.targetLocation in nulls:
            return False
        return True

    def __valLocGrp(self):
        if self.targetSkillRq is not None or self.runTime is not None:
            return False
        validLocs = {const.locChar, const.locShip, const.locTgt, const.locSelf}
        if self.operation in nulls or not self.targetLocation in validLocs or \
        self.targetGroup in nulls:
            return False
        return True

    def __valLoc(self):
        if self.targetGroup is not None or self.targetSkillRq is not None or \
        self.runTime is not None:
            return False
        validLocs = {const.locChar, const.locShip, const.locTgt, const.locSelf}
        if self.operation in nulls or not self.targetLocation in validLocs:
            return False
        return True

    def __valLocSrq(self):
        if self.targetGroup is not None or self.runTime is not None:
            return False
        validLocs = {const.locChar, const.locShip, const.locTgt, const.locSelf}
        if self.operation in nulls or not self.targetLocation in validLocs or \
        self.targetSkillRq in nulls:
            return False
        return True

    def __valOwnSrq(self):
        if self.targetGroup is not None or self.runTime is not None:
            return False
        validLocs = {const.locChar, const.locShip}
        if self.operation in nulls or not self.targetLocation in validLocs or \
        self.targetSkillRq in nulls:
            return False
        return True

    def __valInstant(self):
        if self.operation is not None or self.targetGroup is not None or \
        self.targetSkillRq is not None:
            return False
        validRunTimes = {const.infoPre, const.infoPost}
        if self.targetLocation in nulls or not self.runTime in validRunTimes:
            return False
        return True

    def isMirrorToPost(self, other):
        """For duration modification, return True if passed post-modifier complements self, pre-modifier"""
        # First, check type, it should be duration modification for both,
        # as only they have do-undo pair
        if len({self.type, other.type}.intersection(durationMods)) < 2:
            return False
        # After, check actual mirror type according to map
        if self.type in mirrorDurationMods:
            if other.type != mirrorDurationMods[self.type]:
                return False
        # Without appropriate entry in mirror dictionary, consider it as
        # non-mirror mod
        else:
            return False
        # Passed post-modifier should have no conditions assigned to it; they should be de-applied w/o
        # any condition, our approach to this assumes it
        if other.conditions is not None:
            return False
        # Then, check all other fields of modifier
        if self.sourceAttribute != other.sourceAttribute or self.operation != other.operation or \
        self.targetAttribute != other.targetAttribute or self.targetLocation != other.targetLocation or \
        self.targetGroup != other.targetGroup or self.targetSkillRq != other.targetSkillRq:
            return False
        # If all conditions were met, then it's actually mirror
        return True

    # Set of conversion methods
    def convertToInfo(self):
        """Convert Modifier object to EffectInfo object"""
        # Create object and fill generic fields
        info = EffectInfo()
        info.conditions = self.conditions
        info.sourceAttributeId = self.sourceAttribute
        info.targetAttributeId = self.targetAttribute
        # Fill remaining fields on per-modifier basis
        conversionMap = {const.opndAddGangGrpMod: self.__convGangGrp,
                         const.opndRmGangGrpMod: self.__convGangGrp,
                         const.opndAddGangItmMod: self.__convGangItm,
                         const.opndRmGangItmMod: self.__convGangItm,
                         const.opndAddGangOwnSrqMod: self.__convGangOwnSrq,
                         const.opndRmGangOwnSrqMod: self.__convGangOwnSrq,
                         const.opndAddGangSrqMod: self.__convGangSrq,
                         const.opndRmGangSrqMod: self.__convGangSrq,
                         const.opndAddItmMod: self.__convItm,
                         const.opndRmItmMod: self.__convItm,
                         const.opndAddLocGrpMod: self.__convLocGrp,
                         const.opndRmLocGrpMod: self.__convLocGrp,
                         const.opndAddLocMod: self.__convLoc,
                         const.opndRmLocMod: self.__convLoc,
                         const.opndAddLocSrqMod: self.__convLocSrq,
                         const.opndRmLocSrqMod: self.__convLocSrq,
                         const.opndAddOwnSrqMod: self.__convOwnSrq,
                         const.opndRmOwnSrqMod: self.__convOwnSrq,
                         const.opndAssign: self.__convAssign,
                         const.opndInc: self.__convInc,
                         const.opndDec: self.__convDec}
        conversionMap[self.type](info)
        return info

    def __convGangGrp(self, info):
        info.type = const.infoDuration
        info.gang = True
        info.operation = self.operation
        info.location = const.locShip
        info.filterType = const.filterGroup
        info.filterValue = self.targetGroup

    def __convGangItm(self, info):
        info.type = const.infoDuration
        info.gang = True
        info.operation = self.operation
        info.location = const.locShip

    def __convGangOwnSrq(self, info):
        info.type = const.infoDuration
        info.gang = True
        info.operation = self.operation
        info.location = const.locSpace
        info.filterType = const.filterSkill
        info.filterValue = self.targetSkillRq

    def __convGangSrq(self, info):
        info.type = const.infoDuration
        info.gang = True
        info.operation = self.operation
        info.location = const.locShip
        info.filterType = const.filterSkill
        info.filterValue = self.targetSkillRq

    def __convItm(self, info):
        info.type = const.infoDuration
        info.operation = self.operation
        info.location = self.targetLocation

    def __convLocGrp(self, info):
        info.type = const.infoDuration
        info.operation = self.operation
        info.location = self.targetLocation
        info.filterType = const.filterGroup
        info.filterValue = self.targetGroup

    def __convLoc(self, info):
        info.type = const.infoDuration
        info.operation = self.operation
        info.location = self.targetLocation
        info.filterType = const.filterAll

    def __convLocSrq(self, info):
        info.type = const.infoDuration
        info.operation = self.operation
        info.location = self.targetLocation
        info.filterType = const.filterSkill
        info.filterValue = self.targetSkillRq

    def __convOwnSrq(self, info):
        info.type = const.infoDuration
        info.operation = self.operation
        info.location = const.locSpace
        info.filterType = const.filterSkill
        info.filterValue = self.targetSkillRq

    def __convAssign(self, info):
        info.type = self.runTime
        info.operation = const.optrAssign
        info.location = self.targetLocation

    def __convInc(self, info):
        info.type = self.runTime
        info.operation = const.optrIncr
        info.location = self.targetLocation

    def __convDec(self, info):
        info.type = self.runTime
        info.operation = const.optrDecr
        info.location = self.targetLocation
