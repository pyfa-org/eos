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


from eos.const import Operand, EffectCategory
from eos.calc.info.info import Info, InfoState, InfoContext, InfoRunTime, InfoLocation, InfoFilterType, InfoOperator, InfoSourceType
from .modifierBuilder import ModifierBuilder
from .operandData import operandData, OperandType


# Dictionary which assists conversion of effect category
# and operand gang/local modification to state and context
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


class InfoBuildStatus:
    """Effect info building status ID holder"""
    notParsed = 1  # Expression trees were not parsed into infos yet
    error = 2  # Errors occurred during expression trees parsing or validation
    okPartial = 3  # Infos were generated, but some of modifications were dropped as unsupported
    okFull = 4  # All modifications were pulled out of expression tree successfully


class InfoBuilder:
    """
    Class is responsible for converting Modifier objects into Info objects,
    which can then be used in the rest of the engine.
    """

    def build(self, preExpression, postExpression, effectCategoryId):
        """
        Generate Info objects out of passed data.

        Positional arguments:
        preExpression -- root node of preExpression
        postExpression -- root node of postExpression
        effectCategoryId -- effect category ID for which we're making infos

        Return value:
        Tuple (set with Info objects, build status), where build status
        is InfoLocation class' attribute value
        """
        # By default, assume that our build is 100% successful
        buildStatus = InfoBuildStatus.okFull
        # Make instance of modifier builder and get modifiers out
        # of both trees
        modBuilder = ModifierBuilder()
        preMods, skippedData = modBuilder.build(preExpression, InfoRunTime.pre, effectCategoryId)
        # If any skipped data was encountered, change build status
        if skippedData is True:
            buildStatus = InfoBuildStatus.okPartial
        postMods, skippedData = modBuilder.build(postExpression, InfoRunTime.post, effectCategoryId)
        if skippedData is True:
            buildStatus = InfoBuildStatus.okPartial
        # Check modifiers we've got for validity
        for modSet in (preMods, postMods):
            for modifier in modSet:
                if self.validateModifier(modifier) is not True:
                    # If any is invalid, return empty set
                    # and error status
                    return set(), InfoBuildStatus.error

        # Container for actual info objects
        infos = set()
        # Helper containers for modifier->info conversion process
        # Contains references to already used for generation
        # of infos pre-modifiers
        usedPres = set()
        # Same for post-modifiers
        usedPosts = set()

        # To get all duration infos, we need two mirror duration modifiers,
        # modifier which applies and modifier which undos effect; cycle through
        # pre-modifiers, which are applying ones
        for preMod in preMods:
            # Skip all non-duration modifiers, we're not interested
            # in them for now. We could avoid this check, as mirror
            # check includes it too, but it would need to be done
            # multiple times, when doing this one time per one preMod
            # is enough.
            try:
                modData = operandData[preMod.type]
            except KeyError:
                modType = None
            else:
                modType = modData.type
            if modType != OperandType.duration:
                continue
            # Cycle through post-modifiers
            for postMod in postMods:
                # Skip modifiers which we already used
                if postMod in usedPosts:
                    continue
                # If matching pre- and post-modifiers were detected
                if self.isMirrorToPost(preMod, postMod) is True:
                    # Create actual info
                    info = self.convertToInfo(preMod)
                    infos.add(info)
                    # Mark used modifiers as used
                    usedPres.add(preMod)
                    usedPosts.add(postMod)
                    # We found  what we've been looking for in this postMod loop, thus bail
                    break

        # Time of instantly-applied modifiers; first, the ones
        # applied in the beginning of the cycle
        for preMod in preMods:
            # Skip non-instant modifier types
            try:
                modData = operandData[preMod.type]
            except KeyError:
                modType = None
            else:
                modType = modData.type
            if modType != OperandType.instant:
                continue
            # Make actual info object
            info = self.convertToInfo(preMod)
            infos.add(info)
            # And mark pre-modifier as used
            usedPres.add(preMod)

        # Same for instant modifiers, applied in the end of
        # module cycle
        for postMod in postMods:
            try:
                modData = operandData[postMod.type]
            except KeyError:
                modType = None
            else:
                modType = modData.type
            if modType != OperandType.instant:
                continue
            info = self.convertToInfo(postMod)
            infos.add(info)
            usedPosts.add(postMod)

        # If there're any pre-modifiers which were not used for
        # info generation, mark current effect as partially parsed
        if len(preMods.difference(usedPres)) > 0:
            buildStatus = InfoBuildStatus.okPartial
        # Same for post-modifiers
        if len(postMods.difference(usedPosts)) > 0:
            buildStatus = InfoBuildStatus.okPartial

        return infos, buildStatus

    def validateModifier(self, modifier):
        """
        Validation for modifier objects. Run few top-level modifier type-agnostic
        checks and then route to type-specific check methods.

        Positional arguments:
        modifier -- modifier for validation

        Return value:
        False if top-level checks fail, false if no type-specific check
        method isn't found, else transmit value returned by check method
        """
        # Target always must be filled
        if modifier.targetAttributeId is None:
            return False
        # Check condition tree
        if modifier.conditions is not None:
            if modifier.conditions.validateTree() is not True:
                return False
        # It should be possible to convert gang flag and effect
        # category ID into state and context
        try:
            operandMeta = operandData[modifier.type]
        except KeyError:
            gangFlag = None
        else:
            gangFlag = operandMeta.gang
        if not (modifier.effectCategoryId, gangFlag) in stateData:
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
            method = validateMap[modifier.type]
        except KeyError:
            return False
        return method(modifier)

    # Block with validating methods, called depending on modifier type
    def __validateGangGrp(self, modifier):
        if (modifier.targetLocation is not None or modifier.targetSkillRequirementId is not None or
            modifier.runTime is not None):
            return False
        if (modifier.sourceType != InfoSourceType.attribute or modifier.sourceValue is None or
            modifier.operator is None or modifier.targetGroupId is None):
            return False
        return True

    def __validateGangItm(self, modifier):
        if (modifier.targetGroupId is not None or modifier.targetSkillRequirementId is not None or
            modifier.targetLocation is not None or modifier.runTime is not None):
            return False
        if (modifier.sourceType != InfoSourceType.attribute or modifier.sourceValue is None or
            modifier.operator is None):
            return False
        return True

    def __validateGangOwnSrq(self, modifier):
        if (modifier.targetLocation is not None or modifier.targetGroupId is not None or
            modifier.runTime is not None):
            return False
        if (modifier.sourceType != InfoSourceType.attribute or modifier.sourceValue is None or
            modifier.operator is None or modifier.targetSkillRequirementId is None):
            return False
        return True

    def __validateGangSrq(self, modifier):
        if (modifier.targetLocation is not None or modifier.targetGroupId is not None or
            modifier.runTime is not None):
            return False
        if (modifier.sourceType != InfoSourceType.attribute or modifier.sourceValue is None or
            modifier.operator is None or modifier.targetSkillRequirementId is None):
            return False
        return True

    def __validateItm(self, modifier):
        if (modifier.targetGroupId is not None or modifier.targetSkillRequirementId is not None or
            modifier.runTime is not None):
            return False
        if (modifier.sourceType != InfoSourceType.attribute or modifier.sourceValue is None or
            modifier.operator is None or modifier.targetLocation is None):
            return False
        return True

    def __validateLocGrp(self, modifier):
        if modifier.targetSkillRequirementId is not None or modifier.runTime is not None:
            return False
        validLocs = {InfoLocation.character, InfoLocation.ship, InfoLocation.target, InfoLocation.self_}
        if (modifier.sourceType != InfoSourceType.attribute or modifier.sourceValue is None or
            modifier.operator is None or not modifier.targetLocation in validLocs or
            modifier.targetGroupId is None):
            return False
        return True

    def __validateLoc(self, modifier):
        if (modifier.targetGroupId is not None or modifier.targetSkillRequirementId is not None or
            modifier.runTime is not None):
            return False
        validLocs = {InfoLocation.character, InfoLocation.ship, InfoLocation.target, InfoLocation.self_}
        if (modifier.sourceType != InfoSourceType.attribute or modifier.sourceValue is None or
            modifier.operator is None or not modifier.targetLocation in validLocs):
            return False
        return True

    def __validateLocSrq(self, modifier):
        if modifier.targetGroupId is not None or modifier.runTime is not None:
            return False
        validLocs = {InfoLocation.character, InfoLocation.ship, InfoLocation.target, InfoLocation.self_}
        if (modifier.sourceType != InfoSourceType.attribute or modifier.sourceValue is None or
            modifier.operator is None or not modifier.targetLocation in validLocs or
            modifier.targetSkillRequirementId is None):
            return False
        return True

    def __validateOwnSrq(self, modifier):
        if modifier.targetGroupId is not None or modifier.runTime is not None:
            return False
        validLocs = {InfoLocation.character, InfoLocation.ship}
        if (modifier.sourceType != InfoSourceType.attribute or modifier.sourceValue is None or
            modifier.operator is None or not modifier.targetLocation in validLocs or
            modifier.targetSkillRequirementId is None):
            return False
        return True

    def __validateInstant(self, modifier):
        if (modifier.operator is not None or modifier.targetGroupId is not None or
            modifier.targetSkillRequirementId is not None):
            return False
        validSrcTypes = {InfoSourceType.attribute, InfoSourceType.value}
        validRunTimes = {InfoRunTime.pre, InfoRunTime.post}
        # We can either refer some non-zero source attribute, or provide source value directly
        if (not modifier.sourceType in validSrcTypes or not modifier.runTime in validRunTimes or
            (modifier.sourceType == InfoSourceType.attribute and modifier.sourceValue is None) or
            (modifier.sourceType == InfoSourceType.value and modifier.sourceValue is None) or
            modifier.targetLocation is None):
            return False
        return True

    def isMirrorToPost(self, preMod, postMod):
        """
        Check if passed post-modifier is mirror to pre-modifier.

        Positional arguments:
        preMod -- first modifier to check
        postMod -- second modifier to check

        Return value:
        True if postMod complements preMod as removal of duration modification
        complements addition of duration modification (all duration-related
        attributes, besides type, must be the same), else false
        """
        # First, check type, it should be duration modification for both,
        # as only they have do-undo pair
        for modifier in {preMod, postMod}:
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
            modData = operandData[preMod.type]
        except KeyError:
            modMirror = None
        else:
            modMirror = modData.mirror
        if modMirror != postMod.type:
            return False
        # Passed post-modifier should have no conditions assigned to it; they should be de-applied w/o
        # any condition, our approach to this assumes it
        if postMod.conditions is not None:
            return False
        # Then, check all other fields of modifier
        if (preMod.effectCategoryId != postMod.effectCategoryId or preMod.sourceType != postMod.sourceType or
            preMod.sourceValue != postMod.sourceValue or preMod.operator != postMod.operator or
            preMod.targetAttributeId != postMod.targetAttributeId or preMod.targetLocation != postMod.targetLocation or
            preMod.targetGroupId != postMod.targetGroupId or preMod.targetSkillRequirementId != postMod.targetSkillRequirementId):
            return False
        # If all conditions were met, then it's actually mirror
        return True

    def convertToInfo(self, modifier):
        """
        Convert modifier to Info object. Should be called on instant modifiers
        or duration modifiers which describe addition part (removal part normally
        shouldn't include conditions).

        Positional arguments:
        modifier -- modifier for conversion

        Return value:
        Info object, generated out of modifier
        """
        # Create object and fill generic fields
        info = Info()
        info.conditions = modifier.conditions
        info.sourceType = modifier.sourceType
        info.sourceValue = modifier.sourceValue
        info.targetAttributeId = modifier.targetAttributeId
        info.state, info.context = stateData[(modifier.effectCategoryId, operandData[modifier.type].gang)]
        # Fill remaining fields on per-modifier basis
        conversionMap = {Operand.addGangGrpMod: self.__convertGangGrp,
                         Operand.addGangItmMod: self.__convertGangItm,
                         Operand.addGangOwnSrqMod: self.__convertGangOwnSrq,
                         Operand.addGangSrqMod: self.__convertGangSrq,
                         Operand.addItmMod: self.__convertItm,
                         Operand.addLocGrpMod: self.__convertLocGrp,
                         Operand.addLocMod: self.__convertLoc,
                         Operand.addLocSrqMod: self.__convertLocSrq,
                         Operand.addOwnSrqMod: self.__convertOwnSrq,
                         Operand.assign: self.__convertAssign,
                         Operand.inc: self.__convertInc,
                         Operand.dec: self.__convertDec}
        conversionMap[modifier.type](modifier, info)
        return info

    # Block with conversion methods, called depending on modifier type
    def __convertGangGrp(self, modifier, info):
        info.runTime = InfoRunTime.duration
        info.operator = modifier.operator
        info.location = InfoLocation.ship
        info.filterType = InfoFilterType.group
        info.filterValue = modifier.targetGroupId

    def __convertGangItm(self, modifier, info):
        info.runTime = InfoRunTime.duration
        info.operator = modifier.operator
        info.location = InfoLocation.ship

    def __convertGangOwnSrq(self, modifier, info):
        info.runTime = InfoRunTime.duration
        info.operator = modifier.operator
        info.location = InfoLocation.space
        info.filterType = InfoFilterType.skill
        info.filterValue = modifier.targetSkillRequirementId

    def __convertGangSrq(self, modifier, info):
        info.runTime = InfoRunTime.duration
        info.operator = modifier.operator
        info.location = InfoLocation.ship
        info.filterType = InfoFilterType.skill
        info.filterValue = modifier.targetSkillRequirementId

    def __convertItm(self, modifier, info):
        info.runTime = InfoRunTime.duration
        info.operator = modifier.operator
        info.location = modifier.targetLocation

    def __convertLocGrp(self, modifier, info):
        info.runTime = InfoRunTime.duration
        info.operator = modifier.operator
        info.location = modifier.targetLocation
        info.filterType = InfoFilterType.group
        info.filterValue = modifier.targetGroupId

    def __convertLoc(self, modifier, info):
        info.runTime = InfoRunTime.duration
        info.operator = modifier.operator
        info.location = modifier.targetLocation
        info.filterType = InfoFilterType.all_

    def __convertLocSrq(self, modifier, info):
        info.runTime = InfoRunTime.duration
        info.operator = modifier.operator
        info.location = modifier.targetLocation
        info.filterType = InfoFilterType.skill
        info.filterValue = modifier.targetSkillRequirementId

    def __convertOwnSrq(self, modifier, info):
        info.runTime = InfoRunTime.duration
        info.operator = modifier.operator
        info.location = InfoLocation.space
        info.filterType = InfoFilterType.skill
        info.filterValue = modifier.targetSkillRequirementId

    def __convertAssign(self, modifier, info):
        info.runTime = modifier.runTime
        info.operator = InfoOperator.assignment
        info.location = modifier.targetLocation

    def __convertInc(self, modifier, info):
        info.runTime = modifier.runTime
        info.operator = InfoOperator.increment
        info.location = modifier.targetLocation

    def __convertDec(self, modifier, info):
        info.runTime = modifier.runTime
        info.operator = InfoOperator.decrement
        info.location = modifier.targetLocation
