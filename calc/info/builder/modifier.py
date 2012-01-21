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


from eos.const import nulls, Operand, EffectCategory
from eos.calc.info.info import Info, InfoState, InfoContext, InfoRunTime, InfoLocation, InfoFilterType, InfoOperator, InfoSourceType
from .operandData import operandData, OperandType


# Convert effect category and operand gang/local modification
# to state and context
# Format: {(effect category, gang flag): (state, context)}
stateData = {(EffectCategory.passive, False): (InfoState.offline, InfoContext.local),
             (EffectCategory.passive, True): (InfoState.offline, InfoContext.gang),
             (EffectCategory.active, False): (InfoState.active, InfoContext.local),
             (EffectCategory.active, True): (InfoState.active, InfoContext.gang),
             (EffectCategory.target, False): (InfoState.active, InfoContext.projected),
             (EffectCategory.online, False): (InfoState.online, InfoContext.local),
             (EffectCategory.online, True): (InfoState.online, InfoContext.gang),
             (EffectCategory.overload, False): (InfoState.overload, InfoContext.local),
             (EffectCategory.overload, True): (InfoState.overload, InfoContext.gang),
             (EffectCategory.system, False): (InfoState.offline, InfoContext.local),
             (EffectCategory.system, True): (InfoState.offline, InfoContext.gang)}


class Modifier:
    """
    Internal builder object, stores meaningful elements of expression tree
    temporarily and provides facilities to convert them to Info objects
    """

    def __init__(self):
        # Conditions under which modification is applied,
        # must be None or tree of condition Atom objects.
        self.conditions = None
        # Type of modification, must be Operand class' attribute value,
        # only those which describe some operation applied onto item
        # (belonging to either durationMods orinstantMods sets).
        self.type = None
        # Keeps category ID of effect from whose expressions it
        # was generated
        self.effectCategoryId = None
        # Describes when modification should be applied, for instant
        # modifications only:
        # For modifier types, belonging to instant, must be
        # InfoRunTime.pre or InfoRunTime.post;
        # For other modifier types, must be None.
        self.runTime = None
        # Target location to change:
        # For modifier types belonging to gang group, must be None
        # For other modifier types must be InfoLocation class'
        # attribute value.
        self.targetLocation = None
        # Which operation should be applied during modification,
        # must be InfoOperator class' attribute value.
        self.operator = None
        # Which attribute will be affected by operator on the target,
        # must be integer which refers attribute via ID.
        self.targetAttributeId = None
        # Items only belonging to this group will be affected by
        # modification:
        # For modifier types, which include group filter, must be integer
        # which refers group via ID;
        # For other modifier types must be None.
        self.targetGroupId = None
        # Items only having this skill requirement will be affected by
        # modification:
        # For modifier types, which include skill requirement filter,
        # must be integer which refers type via ID, or const.Type.self_
        # to refer type of info carrier
        # For other modifier types must be None.
        self.targetSkillRequirementId = None
        # SourceValue type, must be InfoSourceType class'
        # attribute value.
        self.sourceType = None
        # Value which is used as modification value for operation:
        # For sourceType.attribute must be integer which refers attribute via ID;
        # For sourceType.value must be any value CCP can define in expression, integer or value.
        self.sourceValue = None

    def validate(self):
        """
        Self-validation for modifier objects. Run few top-level modifier
        type-agnostic checks and then route to type-specific check methods.

        Return value:
        False if top-level checks fail, false if no type-specific check
        method isn't found, else transmit value returned by check method
        """
        # Target always must be filled
        if self.targetAttributeId in nulls:
            return False
        # Check condition tree
        if self.conditions is not None:
            if self.conditions.validateTree() is not True:
                return False
        # It should be possible to convert gang flag and effect
        # category ID into state and context
        try:
            operandMeta = operandData[self.type]
        except KeyError:
            gangFlag = None
        else:
            gangFlag = operandMeta.gang
        if not (self.effectCategoryId, gangFlag) in stateData:
            return False
        # Other fields are optional, check them using modifier type
        validateMap = {Operand.addGangGrpMod: self.__validateGangGrp,
                       Operand.rmGangGrpMod: self.__validateGangGrp,
                       Operand.addGangItmMod: self.__validateGangItm,
                       Operand.rmGangItmMod: self.__validateGangItm,
                       Operand.addGangOwnSrqMod: self.__validateGangOwnSrq,
                       Operand.rmGangOwnSrqMod: self.__validateGangOwnSrq,
                       Operand.addGangSrqMod: self.__validateGangSrq,
                       Operand.rmGangSrqMod: self.__validateGangSrq,
                       Operand.addItmMod: self.__validateItm,
                       Operand.rmItmMod: self.__validateItm,
                       Operand.addLocGrpMod: self.__validateLocGrp,
                       Operand.rmLocGrpMod: self.__validateLocGrp,
                       Operand.addLocMod: self.__validateLoc,
                       Operand.rmLocMod: self.__validateLoc,
                       Operand.addLocSrqMod: self.__validateLocSrq,
                       Operand.rmLocSrqMod: self.__validateLocSrq,
                       Operand.addOwnSrqMod: self.__validateOwnSrq,
                       Operand.rmOwnSrqMod: self.__validateOwnSrq,
                       Operand.assign: self.__validateInstant,
                       Operand.inc: self.__validateInstant,
                       Operand.dec: self.__validateInstant}
        try:
            method = validateMap[self.type]
        except KeyError:
            return False
        return method()

    # Block with validating methods, called depending on modifier type
    def __validateGangGrp(self):
        if (self.targetLocation is not None or self.targetSkillRequirementId is not None or
            self.runTime is not None):
            return False
        if (self.sourceType != InfoSourceType.attribute or self.sourceValue in nulls or
            self.operator in nulls or self.targetGroupId in nulls):
            return False
        return True

    def __validateGangItm(self):
        if (self.targetGroupId is not None or self.targetSkillRequirementId is not None or
            self.targetLocation is not None or self.runTime is not None):
            return False
        if (self.sourceType != InfoSourceType.attribute or self.sourceValue in nulls or
            self.operator in nulls):
            return False
        return True

    def __validateGangOwnSrq(self):
        if (self.targetLocation is not None or self.targetGroupId is not None or
            self.runTime is not None):
            return False
        if (self.sourceType != InfoSourceType.attribute or self.sourceValue in nulls or
            self.operator in nulls or self.targetSkillRequirementId in nulls):
            return False
        return True

    def __validateGangSrq(self):
        if (self.targetLocation is not None or self.targetGroupId is not None or
            self.runTime is not None):
            return False
        if (self.sourceType != InfoSourceType.attribute or self.sourceValue in nulls or
            self.operator in nulls or self.targetSkillRequirementId in nulls):
            return False
        return True

    def __validateItm(self):
        if (self.targetGroupId is not None or self.targetSkillRequirementId is not None or
            self.runTime is not None):
            return False
        if (self.sourceType != InfoSourceType.attribute or self.sourceValue in nulls or
            self.operator in nulls or self.targetLocation in nulls):
            return False
        return True

    def __validateLocGrp(self):
        if self.targetSkillRequirementId is not None or self.runTime is not None:
            return False
        validLocs = {InfoLocation.character, InfoLocation.ship, InfoLocation.target, InfoLocation.self_}
        if (self.sourceType != InfoSourceType.attribute or self.sourceValue in nulls or
            self.operator in nulls or not self.targetLocation in validLocs or
            self.targetGroupId in nulls):
            return False
        return True

    def __validateLoc(self):
        if (self.targetGroupId is not None or self.targetSkillRequirementId is not None or
            self.runTime is not None):
            return False
        validLocs = {InfoLocation.character, InfoLocation.ship, InfoLocation.target, InfoLocation.self_}
        if (self.sourceType != InfoSourceType.attribute or self.sourceValue in nulls or
            self.operator in nulls or not self.targetLocation in validLocs):
            return False
        return True

    def __validateLocSrq(self):
        if self.targetGroupId is not None or self.runTime is not None:
            return False
        validLocs = {InfoLocation.character, InfoLocation.ship, InfoLocation.target, InfoLocation.self_}
        if (self.sourceType != InfoSourceType.attribute or self.sourceValue in nulls or
            self.operator in nulls or not self.targetLocation in validLocs or
            self.targetSkillRequirementId in nulls):
            return False
        return True

    def __validateOwnSrq(self):
        if self.targetGroupId is not None or self.runTime is not None:
            return False
        validLocs = {InfoLocation.character, InfoLocation.ship}
        if (self.sourceType != InfoSourceType.attribute or self.sourceValue in nulls or
            self.operator in nulls or not self.targetLocation in validLocs or
            self.targetSkillRequirementId in nulls):
            return False
        return True

    def __validateInstant(self):
        if (self.operator is not None or self.targetGroupId is not None or
            self.targetSkillRequirementId is not None):
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
        """
        Check if both duration modifiers actually do the same thing

        Positional arguments:
        other -- other modifier to compare with self

        Return value:
        True if both modifiers are duration and all their duration-related
        attributes are the same, else False
        """
        # Check if both are duration modifiers
        for modifier in {self, other}:
            try:
                modData = operandData[modifier.type]
            except KeyError:
                modType = None
            else:
                modType = modData.type
            if modType != OperandType.duration:
                return False
        # Check all modifier fields that make the difference for duration modifiers
        if (self.type != other.type or self.effectCategoryId != other.effectCategoryId or
            self.sourceType != other.sourceType or self.sourceValue != other.sourceValue or
            self.operator != other.operator or self.targetAttributeId != other.targetAttributeId or
            self.targetLocation != other.targetLocation or self.targetGroupId != other.targetGroupId or
            self.targetSkillRequirementId != other.targetSkillRequirementId):
            return False
        # They're the same if above conditions were passed, other fields irrelevant
        return True

    def isMirrorToPost(self, other):
        """
        Check if passed post-modifier is mirror to self

        Positional arguments:
        other -- other modifier to check

        Return value:
        True if other complements self as removal of duration modification
        complements addition of duration modification (all duration-related
        attributes, besides type, must be the same), else false
        """
        # First, check type, it should be duration modification for both,
        # as only they have do-undo pair
        for modifier in {self, other}:
            try:
                modData = operandData[modifier.type]
            except KeyError:
                modType = None
            else:
                modType = modData.type
            if modType != OperandType.duration:
                return False
        # After, check actual mirror
        try:
            modData = operandData[self.type]
        except KeyError:
            modMirror = None
        else:
            modMirror = modData.mirror
        if modMirror != other.type:
            return False
        # Passed post-modifier should have no conditions assigned to it; they should be de-applied w/o
        # any condition, our approach to this assumes it
        if other.conditions is not None:
            return False
        # Then, check all other fields of modifier
        if (self.effectCategoryId != other.effectCategoryId or self.sourceType != other.sourceType or
            self.sourceValue != other.sourceValue or self.operator != other.operator or
            self.targetAttributeId != other.targetAttributeId or self.targetLocation != other.targetLocation
            or self.targetGroupId != other.targetGroupId or self.targetSkillRequirementId != other.targetSkillRequirementId):
            return False
        # If all conditions were met, then it's actually mirror
        return True

    def convertToInfo(self):
        """
        Convert modifier to Info object. Should be called on instant modifiers
        or duration modifiers which describe addition part (removal part normally
        shouldn't include conditions).

        Return value:
        Info object, generated out of modifier
        """
        # Create object and fill generic fields
        info = Info()
        info.conditions = self.conditions
        info.sourceType = self.sourceType
        info.sourceValue = self.sourceValue
        info.targetAttributeId = self.targetAttributeId
        info.state, info.context = stateData[(self.effectCategoryId, operandData[self.type].gang)]
        # Fill remaining fields on per-modifier basis
        conversionMap = {Operand.addGangGrpMod: self.__convertGangGrp,
                         Operand.rmGangGrpMod: self.__convertGangGrp,
                         Operand.addGangItmMod: self.__convertGangItm,
                         Operand.rmGangItmMod: self.__convertGangItm,
                         Operand.addGangOwnSrqMod: self.__convertGangOwnSrq,
                         Operand.rmGangOwnSrqMod: self.__convertGangOwnSrq,
                         Operand.addGangSrqMod: self.__convertGangSrq,
                         Operand.rmGangSrqMod: self.__convertGangSrq,
                         Operand.addItmMod: self.__convertItm,
                         Operand.rmItmMod: self.__convertItm,
                         Operand.addLocGrpMod: self.__convertLocGrp,
                         Operand.rmLocGrpMod: self.__convertLocGrp,
                         Operand.addLocMod: self.__convertLoc,
                         Operand.rmLocMod: self.__convertLoc,
                         Operand.addLocSrqMod: self.__convertLocSrq,
                         Operand.rmLocSrqMod: self.__convertLocSrq,
                         Operand.addOwnSrqMod: self.__convertOwnSrq,
                         Operand.rmOwnSrqMod: self.__convertOwnSrq,
                         Operand.assign: self.__convertAssign,
                         Operand.inc: self.__convertInc,
                         Operand.dec: self.__convertDec}
        conversionMap[self.type](info)
        return info

    # Block with conversion methods, called depending on modifier type
    def __convertGangGrp(self, info):
        info.runTime = InfoRunTime.duration
        info.operator = self.operator
        info.location = InfoLocation.ship
        info.filterType = InfoFilterType.group
        info.filterValue = self.targetGroupId

    def __convertGangItm(self, info):
        info.runTime = InfoRunTime.duration
        info.operator = self.operator
        info.location = InfoLocation.ship

    def __convertGangOwnSrq(self, info):
        info.runTime = InfoRunTime.duration
        info.operator = self.operator
        info.location = InfoLocation.space
        info.filterType = InfoFilterType.skill
        info.filterValue = self.targetSkillRequirementId

    def __convertGangSrq(self, info):
        info.runTime = InfoRunTime.duration
        info.operator = self.operator
        info.location = InfoLocation.ship
        info.filterType = InfoFilterType.skill
        info.filterValue = self.targetSkillRequirementId

    def __convertItm(self, info):
        info.runTime = InfoRunTime.duration
        info.operator = self.operator
        info.location = self.targetLocation

    def __convertLocGrp(self, info):
        info.runTime = InfoRunTime.duration
        info.operator = self.operator
        info.location = self.targetLocation
        info.filterType = InfoFilterType.group
        info.filterValue = self.targetGroupId

    def __convertLoc(self, info):
        info.runTime = InfoRunTime.duration
        info.operator = self.operator
        info.location = self.targetLocation
        info.filterType = InfoFilterType.all_

    def __convertLocSrq(self, info):
        info.runTime = InfoRunTime.duration
        info.operator = self.operator
        info.location = self.targetLocation
        info.filterType = InfoFilterType.skill
        info.filterValue = self.targetSkillRequirementId

    def __convertOwnSrq(self, info):
        info.runTime = InfoRunTime.duration
        info.operator = self.operator
        info.location = InfoLocation.space
        info.filterType = InfoFilterType.skill
        info.filterValue = self.targetSkillRequirementId

    def __convertAssign(self, info):
        info.runTime = self.runTime
        info.operator = InfoOperator.assignment
        info.location = self.targetLocation

    def __convertInc(self, info):
        info.runTime = self.runTime
        info.operator = InfoOperator.increment
        info.location = self.targetLocation

    def __convertDec(self, info):
        info.runTime = self.runTime
        info.operator = InfoOperator.decrement
        info.location = self.targetLocation
