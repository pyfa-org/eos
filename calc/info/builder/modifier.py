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


from eos.const import nulls, Operand
from eos.calc.info.info import Info, InfoRunTime, InfoLocation, InfoFilterType, InfoOperator, InfoSourceType
from .builderData import durationMods, mirrorDurationMods


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
        # Source type, attribute or direct value
        self.sourceType = None
        # Source value
        self.sourceValue = None
        # Operation to be applied on target
        self.operator = None
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
        # Target always should be filled
        if self.targetAttribute in nulls:
            return False
        # Check condition tree
        if self.conditions is not None:
            if self.conditions.validateTree() is not True:
                return False
        # Other fields are optional, check them using modifier type
        validateMap = {Operand.addGangGrpMod: self.__valGangGrp,
                       Operand.rmGangGrpMod: self.__valGangGrp,
                       Operand.addGangItmMod: self.__valGangItm,
                       Operand.rmGangItmMod: self.__valGangItm,
                       Operand.addGangOwnSrqMod: self.__valGangOwnSrq,
                       Operand.rmGangOwnSrqMod: self.__valGangOwnSrq,
                       Operand.addGangSrqMod: self.__valGangSrq,
                       Operand.rmGangSrqMod: self.__valGangSrq,
                       Operand.addItmMod: self.__valItm,
                       Operand.rmItmMod: self.__valItm,
                       Operand.addLocGrpMod: self.__valLocGrp,
                       Operand.rmLocGrpMod: self.__valLocGrp,
                       Operand.addLocMod: self.__valLoc,
                       Operand.rmLocMod: self.__valLoc,
                       Operand.addLocSrqMod: self.__valLocSrq,
                       Operand.rmLocSrqMod: self.__valLocSrq,
                       Operand.addOwnSrqMod: self.__valOwnSrq,
                       Operand.rmOwnSrqMod: self.__valOwnSrq,
                       Operand.assign: self.__valInstant,
                       Operand.inc: self.__valInstant,
                       Operand.dec: self.__valInstant}
        try:
            method = validateMap[self.type]
        except KeyError:
            return False
        return method()

    def __valGangGrp(self):
        if (self.targetLocation is not None or self.targetSkillRq is not None or
            self.runTime is not None):
            return False
        if (self.sourceType != InfoSourceType.attribute or self.sourceValue in nulls or
            self.operator in nulls or self.targetGroup in nulls):
            return False
        return True

    def __valGangItm(self):
        if (self.targetGroup is not None or self.targetSkillRq is not None or
            self.targetLocation is not None or self.runTime is not None):
            return False
        if (self.sourceType != InfoSourceType.attribute or self.sourceValue in nulls or
            self.operator in nulls):
            return False
        return True

    def __valGangOwnSrq(self):
        if (self.targetLocation is not None or self.targetGroup is not None or
            self.runTime is not None):
            return False
        if (self.sourceType != InfoSourceType.attribute or self.sourceValue in nulls or
            self.operator in nulls or self.targetSkillRq in nulls):
            return False
        return True

    def __valGangSrq(self):
        if (self.targetLocation is not None or self.targetGroup is not None or
            self.runTime is not None):
            return False
        if (self.sourceType != InfoSourceType.attribute or self.sourceValue in nulls or
            self.operator in nulls or self.targetSkillRq in nulls):
            return False
        return True

    def __valItm(self):
        if (self.targetGroup is not None or self.targetSkillRq is not None or
            self.runTime is not None):
            return False
        if (self.sourceType != InfoSourceType.attribute or self.sourceValue in nulls or
            self.operator in nulls or self.targetLocation in nulls):
            return False
        return True

    def __valLocGrp(self):
        if self.targetSkillRq is not None or self.runTime is not None:
            return False
        validLocs = {InfoLocation.character, InfoLocation.ship, InfoLocation.target, InfoLocation.self_}
        if (self.sourceType != InfoSourceType.attribute or self.sourceValue in nulls or
            self.operator in nulls or not self.targetLocation in validLocs or
            self.targetGroup in nulls):
            return False
        return True

    def __valLoc(self):
        if (self.targetGroup is not None or self.targetSkillRq is not None or
            self.runTime is not None):
            return False
        validLocs = {InfoLocation.character, InfoLocation.ship, InfoLocation.target, InfoLocation.self_}
        if (self.sourceType != InfoSourceType.attribute or self.sourceValue in nulls or
            self.operator in nulls or not self.targetLocation in validLocs):
            return False
        return True

    def __valLocSrq(self):
        if self.targetGroup is not None or self.runTime is not None:
            return False
        validLocs = {InfoLocation.character, InfoLocation.ship, InfoLocation.target, InfoLocation.self_}
        if (self.sourceType != InfoSourceType.attribute or self.sourceValue in nulls or
            self.operator in nulls or not self.targetLocation in validLocs or
            self.targetSkillRq in nulls):
            return False
        return True

    def __valOwnSrq(self):
        if self.targetGroup is not None or self.runTime is not None:
            return False
        validLocs = {InfoLocation.character, InfoLocation.ship}
        if (self.sourceType != InfoSourceType.attribute or self.sourceValue in nulls or
            self.operator in nulls or not self.targetLocation in validLocs or
            self.targetSkillRq in nulls):
            return False
        return True

    def __valInstant(self):
        if (self.operator is not None or self.targetGroup is not None or
            self.targetSkillRq is not None):
            return False
        validSrcTypes = {InfoSourceType.attribute, InfoSourceType.value}
        validRunTimes = {InfoRunTime.pre, InfoRunTime.post}
        # We can either refer some non-zero source attribute, or provide source value directly
        if (not self.sourceType in validSrcTypes or not self.runTime in validRunTimes or
            (self.sourceType == InfoSourceType.attribute and self.sourceValue in nulls) or
            (self.sourceType == InfoSourceType.value and self.sourceValue is None) or
            self.targetLocation in nulls):
            return False
        return True

    def isSameMod(self, other):
        """Return True if both duration modifications actually do the same thing"""
        # Check if both are duration modifiers
        if not self.type in durationMods or not other.type in durationMods:
            return False
        # Check all modifier fields that make the difference for duration modifiers
        if (self.type != other.type or self.sourceType != other.sourceType or
            self.sourceValue != other.sourceValue or self.operator != other.operator or
            self.targetAttribute != other.targetAttribute or self.targetLocation != other.targetLocation or
            self.targetGroup != other.targetGroup or self.targetSkillRq != other.targetSkillRq):
            return False
        # They're the same if above conditions were passed, other fields irrelevant
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
        # non-mirror modifier
        else:
            return False
        # Passed post-modifier should have no conditions assigned to it; they should be de-applied w/o
        # any condition, our approach to this assumes it
        if other.conditions is not None:
            return False
        # Then, check all other fields of modifier
        if (self.sourceType != other.sourceType or self.sourceValue != other.sourceValue or
            self.operator != other.operator or self.targetAttribute != other.targetAttribute or
            self.targetLocation != other.targetLocation or self.targetGroup != other.targetGroup or
            self.targetSkillRq != other.targetSkillRq):
            return False
        # If all conditions were met, then it's actually mirror
        return True

    # Set of conversion methods
    def convertToInfo(self):
        """Convert Modifier object to EffectInfo object"""
        # Create object and fill generic fields
        info = Info()
        info.conditions = self.conditions
        info.sourceType = self.sourceType
        info.sourceValue = self.sourceValue
        info.targetAttribute = self.targetAttribute
        # Fill remaining fields on per-modifier basis
        conversionMap = {Operand.addGangGrpMod: self.__convGangGrp,
                         Operand.rmGangGrpMod: self.__convGangGrp,
                         Operand.addGangItmMod: self.__convGangItm,
                         Operand.rmGangItmMod: self.__convGangItm,
                         Operand.addGangOwnSrqMod: self.__convGangOwnSrq,
                         Operand.rmGangOwnSrqMod: self.__convGangOwnSrq,
                         Operand.addGangSrqMod: self.__convGangSrq,
                         Operand.rmGangSrqMod: self.__convGangSrq,
                         Operand.addItmMod: self.__convItm,
                         Operand.rmItmMod: self.__convItm,
                         Operand.addLocGrpMod: self.__convLocGrp,
                         Operand.rmLocGrpMod: self.__convLocGrp,
                         Operand.addLocMod: self.__convLoc,
                         Operand.rmLocMod: self.__convLoc,
                         Operand.addLocSrqMod: self.__convLocSrq,
                         Operand.rmLocSrqMod: self.__convLocSrq,
                         Operand.addOwnSrqMod: self.__convOwnSrq,
                         Operand.rmOwnSrqMod: self.__convOwnSrq,
                         Operand.assign: self.__convAssign,
                         Operand.inc: self.__convInc,
                         Operand.dec: self.__convDec}
        conversionMap[self.type](info)
        return info

    def __convGangGrp(self, info):
        info.runTime = InfoRunTime.duration
        info.gang = True
        info.operator = self.operator
        info.location = InfoLocation.ship
        info.filterType = InfoFilterType.group
        info.filterValue = self.targetGroup

    def __convGangItm(self, info):
        info.runTime = InfoRunTime.duration
        info.gang = True
        info.operator = self.operator
        info.location = InfoLocation.ship

    def __convGangOwnSrq(self, info):
        info.runTime = InfoRunTime.duration
        info.gang = True
        info.operator = self.operator
        info.location = InfoLocation.space
        info.filterType = InfoFilterType.skill
        info.filterValue = self.targetSkillRq

    def __convGangSrq(self, info):
        info.runTime = InfoRunTime.duration
        info.gang = True
        info.operator = self.operator
        info.location = InfoLocation.ship
        info.filterType = InfoFilterType.skill
        info.filterValue = self.targetSkillRq

    def __convItm(self, info):
        info.runTime = InfoRunTime.duration
        info.operator = self.operator
        info.location = self.targetLocation

    def __convLocGrp(self, info):
        info.runTime = InfoRunTime.duration
        info.operator = self.operator
        info.location = self.targetLocation
        info.filterType = InfoFilterType.group
        info.filterValue = self.targetGroup

    def __convLoc(self, info):
        info.runTime = InfoRunTime.duration
        info.operator = self.operator
        info.location = self.targetLocation
        info.filterType = InfoFilterType.all

    def __convLocSrq(self, info):
        info.runTime = InfoRunTime.duration
        info.operator = self.operator
        info.location = self.targetLocation
        info.filterType = InfoFilterType.skill
        info.filterValue = self.targetSkillRq

    def __convOwnSrq(self, info):
        info.runTime = InfoRunTime.duration
        info.operator = self.operator
        info.location = InfoLocation.space
        info.filterType = InfoFilterType.skill
        info.filterValue = self.targetSkillRq

    def __convAssign(self, info):
        info.runTime = self.runTime
        info.operator = InfoOperator.assignment
        info.location = self.targetLocation

    def __convInc(self, info):
        info.runTime = self.runTime
        info.operator = InfoOperator.increment
        info.location = self.targetLocation

    def __convDec(self, info):
        info.runTime = self.runTime
        info.operator = InfoOperator.decrement
        info.location = self.targetLocation
