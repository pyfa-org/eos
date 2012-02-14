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


from eos.const import Location, State, EffectBuildStatus, Context, RunTime, FilterType, Operator, SourceType, AtomType
from eos.eve.const import Operand, EffectCategory
from .exception import ModifierBuilderException
from .info import Info
from .modifierBuilder import ModifierBuilder
from .helpers import operandData, OperandType


# Dictionary which assists conversion of effect category
# and operand gang/local modification to state and context
# Format: {(effect category, gang flag): (state, context)}
stateData = {(EffectCategory.passive, False): (State.offline, Context.local),
             (EffectCategory.passive, True): (State.offline, Context.gang),
             (EffectCategory.active, False): (State.active, Context.local),
             (EffectCategory.active, True): (State.active, Context.gang),
             (EffectCategory.target, False): (State.active, Context.projected),
             (EffectCategory.online, False): (State.online, Context.local),
             (EffectCategory.online, True): (State.online, Context.gang),
             (EffectCategory.overload, False): (State.overload, Context.local),
             (EffectCategory.overload, True): (State.overload, Context.gang),
             (EffectCategory.system, False): (State.offline, Context.local),
             (EffectCategory.system, True): (State.offline, Context.gang)}


class InfoBuilder:
    """
    Class is responsible for converting Modifier objects into Info objects,
    which can then be used in the rest of the engine.
    """

    @classmethod
    def build(cls, effect, logger):
        """
        Generate Info objects out of passed data.

        Positional arguments:
        effect -- effect, for which we're building infos
        logger -- logger for possible errors

        Return value:
        Tuple (set with Info objects, build status), where build status
        is Location class' attribute value
        """
        # By default, assume that our build is 100% successful
        buildStatus = EffectBuildStatus.okFull
        # Containers for our data
        preMods = set()
        postMods = set()
        # Make instance of modifier builder
        modBuilder = ModifierBuilder()
        # Get modifiers out of both trees
        for tree, runTime, modSet in ((effect.preExpression, RunTime.pre, preMods),
                                      (effect.postExpression, RunTime.post, postMods)):
            try:
                modifiers, skippedData = modBuilder.build(tree, runTime, effect.categoryId)
            # If any errors occurred, return empty set and error status
            except ModifierBuilderException:
                return set(), EffectBuildStatus.error
            except:
                # TODO: This is temporary debugging print, should be moved to logging
                # module when its format is defined
                print("unexpected exception occurred when parsing expression tree with root node ID {}".format(tree.id))
                return set(), EffectBuildStatus.error
            else:
                # Update set with modifiers we've just got
                modSet.update(modifiers)
                # If any skipped data was encountered, change build status
                if skippedData is True:
                    buildStatus = EffectBuildStatus.okPartial
        # Check modifiers we've got for validity
        for modSet in (preMods, postMods):
            for modifier in modSet:
                if cls.validateModifier(modifier) is not True:
                    # If any is invalid, return empty set
                    # and error status
                    return set(), EffectBuildStatus.error

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
                if cls.isMirrorToPost(preMod, postMod) is True:
                    # Create actual info
                    info = cls.convertToInfo(preMod)
                    infos.add(info)
                    # Mark used modifiers as used
                    usedPres.add(preMod)
                    usedPosts.add(postMod)
                    # We found  what we've been looking for in this postMod loop, thus bail
                    break

        # Time of instantly-applied modifiers: the ones which
        # are applied just in the beginning and in the end of cycle
        for modSet, usedMods in ((preMods, usedPres), (postMods, usedPosts)):
            for modifier in modSet:
                # Skip non-instant modifier types
                try:
                    modData = operandData[modifier.type]
                except KeyError:
                    modType = None
                else:
                    modType = modData.type
                if modType != OperandType.instant:
                    continue
                # Make actual info object
                info = cls.convertToInfo(modifier)
                infos.add(info)
                # And mark modifier as used
                usedMods.add(modifier)

        # If there're any modifiers which were not used for
        # info generation, mark current effect as partially parsed
        if len(preMods.difference(usedPres)) > 0 or len(postMods.difference(usedPosts)) > 0:
            buildStatus = EffectBuildStatus.okPartial

        return infos, buildStatus

    @classmethod
    def validateModifier(cls, modifier):
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
            if cls.__validateCondition(modifier.conditions) is not True:
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
        validateMap = {Operand.addGangGrpMod: cls.__validateGangGrp,
                       Operand.rmGangGrpMod: cls.__validateGangGrp,
                       Operand.addGangItmMod: cls.__validateGangItm,
                       Operand.rmGangItmMod: cls.__validateGangItm,
                       Operand.addGangOwnSrqMod: cls.__validateGangOwnSrq,
                       Operand.rmGangOwnSrqMod: cls.__validateGangOwnSrq,
                       Operand.addGangSrqMod: cls.__validateGangSrq,
                       Operand.rmGangSrqMod: cls.__validateGangSrq,
                       Operand.addItmMod: cls.__validateItm,
                       Operand.rmItmMod: cls.__validateItm,
                       Operand.addLocGrpMod: cls.__validateLocGrp,
                       Operand.rmLocGrpMod: cls.__validateLocGrp,
                       Operand.addLocMod: cls.__validateLoc,
                       Operand.rmLocMod: cls.__validateLoc,
                       Operand.addLocSrqMod: cls.__validateLocSrq,
                       Operand.rmLocSrqMod: cls.__validateLocSrq,
                       Operand.addOwnSrqMod: cls.__validateOwnSrq,
                       Operand.rmOwnSrqMod: cls.__validateOwnSrq,
                       Operand.assign: cls.__validateInstant,
                       Operand.inc: cls.__validateInstant,
                       Operand.dec: cls.__validateInstant}
        try:
            method = validateMap[modifier.type]
        except KeyError:
            return False
        return method(modifier)

    # Block with validating methods, called depending on modifier type,
    # plus condition validation methods
    @classmethod
    def __validateGangGrp(cls, modifier):
        if (modifier.targetLocation is not None or modifier.targetSkillRequirementId is not None or
            modifier.runTime is not None):
            return False
        if (modifier.sourceType != SourceType.attribute or modifier.sourceValue is None or
            modifier.operator is None or modifier.targetGroupId is None):
            return False
        return True

    @classmethod
    def __validateGangItm(cls, modifier):
        if (modifier.targetGroupId is not None or modifier.targetSkillRequirementId is not None or
            modifier.targetLocation is not None or modifier.runTime is not None):
            return False
        if (modifier.sourceType != SourceType.attribute or modifier.sourceValue is None or
            modifier.operator is None):
            return False
        return True

    @classmethod
    def __validateGangOwnSrq(cls, modifier):
        if (modifier.targetLocation is not None or modifier.targetGroupId is not None or
            modifier.runTime is not None):
            return False
        if (modifier.sourceType != SourceType.attribute or modifier.sourceValue is None or
            modifier.operator is None or modifier.targetSkillRequirementId is None):
            return False
        return True

    @classmethod
    def __validateGangSrq(cls, modifier):
        if (modifier.targetLocation is not None or modifier.targetGroupId is not None or
            modifier.runTime is not None):
            return False
        if (modifier.sourceType != SourceType.attribute or modifier.sourceValue is None or
            modifier.operator is None or modifier.targetSkillRequirementId is None):
            return False
        return True

    @classmethod
    def __validateItm(cls, modifier):
        if (modifier.targetGroupId is not None or modifier.targetSkillRequirementId is not None or
            modifier.runTime is not None):
            return False
        if (modifier.sourceType != SourceType.attribute or modifier.sourceValue is None or
            modifier.operator is None or modifier.targetLocation is None):
            return False
        return True

    @classmethod
    def __validateLocGrp(cls, modifier):
        if modifier.targetSkillRequirementId is not None or modifier.runTime is not None:
            return False
        validLocs = {Location.character, Location.ship, Location.target, Location.self_}
        if (modifier.sourceType != SourceType.attribute or modifier.sourceValue is None or
            modifier.operator is None or not modifier.targetLocation in validLocs or
            modifier.targetGroupId is None):
            return False
        return True

    @classmethod
    def __validateLoc(cls, modifier):
        if (modifier.targetGroupId is not None or modifier.targetSkillRequirementId is not None or
            modifier.runTime is not None):
            return False
        validLocs = {Location.character, Location.ship, Location.target, Location.self_}
        if (modifier.sourceType != SourceType.attribute or modifier.sourceValue is None or
            modifier.operator is None or not modifier.targetLocation in validLocs):
            return False
        return True

    @classmethod
    def __validateLocSrq(cls, modifier):
        if modifier.targetGroupId is not None or modifier.runTime is not None:
            return False
        validLocs = {Location.character, Location.ship, Location.target, Location.self_}
        if (modifier.sourceType != SourceType.attribute or modifier.sourceValue is None or
            modifier.operator is None or not modifier.targetLocation in validLocs or
            modifier.targetSkillRequirementId is None):
            return False
        return True

    @classmethod
    def __validateOwnSrq(cls, modifier):
        if modifier.targetGroupId is not None or modifier.runTime is not None:
            return False
        validLocs = {Location.character, Location.ship}
        if (modifier.sourceType != SourceType.attribute or modifier.sourceValue is None or
            modifier.operator is None or not modifier.targetLocation in validLocs or
            modifier.targetSkillRequirementId is None):
            return False
        return True

    @classmethod
    def __validateInstant(cls, modifier):
        if (modifier.operator is not None or modifier.targetGroupId is not None or
            modifier.targetSkillRequirementId is not None):
            return False
        validSrcTypes = {SourceType.attribute, SourceType.value}
        validRunTimes = {RunTime.pre, RunTime.post}
        # We can either refer some non-zero source attribute, or provide source value directly
        if (not modifier.sourceType in validSrcTypes or not modifier.runTime in validRunTimes or
            (modifier.sourceType == SourceType.attribute and modifier.sourceValue is None) or
            (modifier.sourceType == SourceType.value and modifier.sourceValue is None) or
            modifier.targetLocation is None):
            return False
        return True

    @classmethod
    def __validateCondition(cls, condition):
        """
        Validate full condition tree, given we're checking top-level node.

        Return value:
        True if tree is valid, False if tree is not valid
        """
        # Top-level node can be either logical join or comparison
        allowedTypes = {AtomType.logic, AtomType.comparison}
        if not condition.type in allowedTypes:
            return False
        return cls.__validateConditionNode(condition)

    @classmethod
    def __validateConditionNode(cls, atom):
        """
        Pick appropriate validation method and run it.

        Return value:
        False if no proper method has been picked, else
        transmit value returned by ran method
        """
        validationRouter = {AtomType.logic: cls.__validateConditionLogic,
                            AtomType.comparison: cls.__validateConditionComparison,
                            AtomType.math: cls.__validateConditionMath,
                            AtomType.valueReference: cls.__validateConditionValueReference,
                            AtomType.value: cls.__validateConditionValue}
        try:
            method = validationRouter[atom.type]
        except KeyError:
            return False
        return method(atom)

    @classmethod
    def __validateConditionLogic(cls, atom):
        if (atom.carrier is not None or atom.attribute is not None or
            atom.value is not None):
            return False
        allowedSubtypes = {AtomType.logic, AtomType.comparison}
        try:
            if not atom.child1.type in allowedSubtypes or not atom.child2.type in allowedSubtypes:
                return False
        except AttributeError:
            return False
        if cls.__validateConditionNode(atom.child1) is not True or cls.__validateConditionNode(atom.child2) is not True:
            return False
        return True

    @classmethod
    def __validateConditionComparison(cls, atom):
        if (atom.carrier is not None or atom.attribute is not None or
            atom.value is not None):
            return False
        allowedSubtypes = {AtomType.math, AtomType.valueReference, AtomType.value}
        try:
            if not atom.child1.type in allowedSubtypes or not atom.child2.type in allowedSubtypes:
                return False
        except AttributeError:
            return False
        if cls.__validateConditionNode(atom.child1) is not True or cls.__validateConditionNode(atom.child2) is not True:
            return False
        return True

    @classmethod
    def __validateConditionMath(cls, atom):
        if (atom.carrier is not None or atom.attribute is not None or
            atom.value is not None):
            return False
        allowedSubtypes = {AtomType.math, AtomType.valueReference, AtomType.value}
        try:
            if not atom.child1.type in allowedSubtypes or not atom.child2.type in allowedSubtypes:
                return False
        except AttributeError:
            return False
        if cls.__validateConditionNode(atom.child1) is not True or cls.__validateConditionNode(atom.child2) is not True:
            return False
        return True

    @classmethod
    def __validateConditionValueReference(cls, atom):
        if (atom.child1 is not None or atom.child2 is not None or
            atom.value is not None):
            return False
        if atom.carrier is None or atom.attribute is None:
            return False
        return True

    @classmethod
    def __validateConditionValue(cls, atom):
        if (atom.child1 is not None or atom.child2 is not None or
            atom.carrier is not None or atom.attribute is not None):
            return False
        if atom.value is None:
            return False
        return True

    @classmethod
    def isMirrorToPost(cls, preMod, postMod):
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

    @classmethod
    def convertToInfo(cls, modifier):
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
        conversionMap = {Operand.addGangGrpMod: cls.__convertGangGrp,
                         Operand.addGangItmMod: cls.__convertGangItm,
                         Operand.addGangOwnSrqMod: cls.__convertGangOwnSrq,
                         Operand.addGangSrqMod: cls.__convertGangSrq,
                         Operand.addItmMod: cls.__convertItm,
                         Operand.addLocGrpMod: cls.__convertLocGrp,
                         Operand.addLocMod: cls.__convertLoc,
                         Operand.addLocSrqMod: cls.__convertLocSrq,
                         Operand.addOwnSrqMod: cls.__convertOwnSrq,
                         Operand.assign: cls.__convertAssign,
                         Operand.inc: cls.__convertInc,
                         Operand.dec: cls.__convertDec}
        conversionMap[modifier.type](modifier, info)
        return info

    # Block with conversion methods, called depending on modifier type
    @classmethod
    def __convertGangGrp(cls, modifier, info):
        info.runTime = RunTime.duration
        info.operator = modifier.operator
        info.location = Location.ship
        info.filterType = FilterType.group
        info.filterValue = modifier.targetGroupId

    @classmethod
    def __convertGangItm(cls, modifier, info):
        info.runTime = RunTime.duration
        info.operator = modifier.operator
        info.location = Location.ship

    @classmethod
    def __convertGangOwnSrq(cls, modifier, info):
        info.runTime = RunTime.duration
        info.operator = modifier.operator
        info.location = Location.space
        info.filterType = FilterType.skill
        info.filterValue = modifier.targetSkillRequirementId

    @classmethod
    def __convertGangSrq(cls, modifier, info):
        info.runTime = RunTime.duration
        info.operator = modifier.operator
        info.location = Location.ship
        info.filterType = FilterType.skill
        info.filterValue = modifier.targetSkillRequirementId

    @classmethod
    def __convertItm(cls, modifier, info):
        info.runTime = RunTime.duration
        info.operator = modifier.operator
        info.location = modifier.targetLocation

    @classmethod
    def __convertLocGrp(cls, modifier, info):
        info.runTime = RunTime.duration
        info.operator = modifier.operator
        info.location = modifier.targetLocation
        info.filterType = FilterType.group
        info.filterValue = modifier.targetGroupId

    @classmethod
    def __convertLoc(cls, modifier, info):
        info.runTime = RunTime.duration
        info.operator = modifier.operator
        info.location = modifier.targetLocation
        info.filterType = FilterType.all_

    @classmethod
    def __convertLocSrq(cls, modifier, info):
        info.runTime = RunTime.duration
        info.operator = modifier.operator
        info.location = modifier.targetLocation
        info.filterType = FilterType.skill
        info.filterValue = modifier.targetSkillRequirementId

    @classmethod
    def __convertOwnSrq(cls, modifier, info):
        info.runTime = RunTime.duration
        info.operator = modifier.operator
        info.location = Location.space
        info.filterType = FilterType.skill
        info.filterValue = modifier.targetSkillRequirementId

    @classmethod
    def __convertAssign(cls, modifier, info):
        info.runTime = modifier.runTime
        info.operator = Operator.assignment
        info.location = modifier.targetLocation

    @classmethod
    def __convertInc(cls, modifier, info):
        info.runTime = modifier.runTime
        info.operator = Operator.increment
        info.location = modifier.targetLocation

    @classmethod
    def __convertDec(cls, modifier, info):
        info.runTime = modifier.runTime
        info.operator = Operator.decrement
        info.location = modifier.targetLocation
