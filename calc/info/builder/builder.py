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


from copy import deepcopy
from itertools import combinations

from eos.const import Type, Operand
from eos.calc.info.info import InfoContext, InfoRunTime, InfoLocation, InfoOperator, InfoSourceType
from .atom import Atom, AtomType, AtomLogicOperator, AtomComparisonOperator, AtomMathOperator
from .builderData import durationMods, instantMods
from .modifier import Modifier


# Operands which are not used in any way in current Eos implementation
inactiveOpnds = {Operand.attack, Operand.cargoScan, Operand.cheatTeleDock,
                 Operand.cheatTeleGate, Operand.aoeDecloak, Operand.ecmBurst,
                 Operand.aoeDmg, Operand.missileLaunch, Operand.defenderLaunch,
                 Operand.fofLaunch, Operand.mine, Operand.powerBooster,
                 Operand.shipScan, Operand.surveyScan, Operand.tgtHostile,
                 Operand.tgtSilent, Operand.toolTgtSkills, Operand.userError,
                 Operand.vrfTgtGrp}


class InfoBuildStatus:
    """Effect info building status ID holder"""
    notParsed = 1  # Expression trees were not parsed into infos yet
    error = 2  # Errors occurred during expression trees parsing or validation
    okPartial = 3  # Infos were generated, but some of modifications were dropped as unsupported
    okFull = 4  # All modifications were pulled out of expression tree successfully


class InfoBuilder:
    """
    Class is responsible for converting two trees (pre and post) of Expression objects (which
    aren't directly useful to us) into EffectInfo objects which can then be used as needed.
    """
    def __init__(self):
        # Modifiers we got out of preExpression
        self.preMods = set()
        # Modifiers we got out of postExpression
        self.postMods = set()
        # Which modifier list we're using at the moment
        self.activeSet = None
        # Which modifier we're referencing at the moment
        self.activeMod = None
        # Conditions applied to all expressions found on current
        # building stage
        self.conditions = None
        # Effect build status
        self.effectStatus = None

    def build(self, preExpression, postExpression, effectCategoryId):
        """Go through both trees and compose our EffectInfos"""
        # Attempt to get context which we'll assign to infos later
        infoContext = InfoContext.effectCategory2context(effectCategoryId)
        # And if it's none, return error right away
        if infoContext is None:
            return set(), InfoBuildStatus.error
        # Else, assume we parse effect 100% successfully by default
        self.effectStatus = InfoBuildStatus.okFull
        # First, we're going to parse pre-expression tree, so set preMods
        # as active set
        self.activeSet = self.preMods
        try:
            # Parse pre-expression tree
            self.__generic(preExpression, None)
        # If any unhandled exceptions occur, return empty set and error code
        except:
            return set(), InfoBuildStatus.error
        # Validate modifiers we've got out of pre-expression tree
        for mod in self.preMods:
            if mod.validate() is not True:
                return set(), InfoBuildStatus.error

        # Do the same for post-expressions
        self.activeSet = self.postMods
        try:
            self.__generic(postExpression, None)
        except:
            return set(), InfoBuildStatus.error
        for mod in self.postMods:
            if mod.validate() is not True:
                return set(), InfoBuildStatus.error

        # Unify multiple modifiers which do the same thing, but under different
        # conditions, into single modifiers. We need this for pre-modifiers only,
        # as post-modifiers shouldn't contain conditions by definition
        self.__builderDurationUnifier(self.preMods)

        # Actual container for info objects
        infos = set()
        # Helper containers for modifier->info conversion process
        # Contains references to already used for generation of infos pre-modifiers
        usedPres = set()
        # Same for post-modifiers
        usedPosts = set()

        # To get all duration infos, we need two mirror duration modifiers,
        # modifier which applies and modifier which undos effect; cycle through
        # pre-modifiers, which are applying ones
        for preMod in self.preMods:
            # Skip all non-duration mods, we're not interested in them for now
            if not preMod.type in durationMods:
                continue
            # Cycle through post-modifiers
            for postMod in self.postMods:
                # Skip modifiers which we already used
                if postMod in usedPosts:
                    continue
                # If matching pre- and post-modifiers were detected
                if preMod.isMirrorToPost(postMod) is True:
                    # Create actual info
                    info = preMod.convertToInfo()
                    infos.add(info)
                    # Mark used modifiers as used
                    usedPres.add(preMod)
                    usedPosts.add(postMod)
                    # We found  what we've been looking for in this postMod loop, thus bail
                    break

        # Time of instantly-applied modifiers; first, the ones
        # applied in the beginning of the cycle
        for preMod in self.preMods:
            # Skip non-instant modifier types
            if not preMod.type in instantMods:
                continue
            # Make actual info object
            info = preMod.convertToInfo()
            infos.add(info)
            # And mark pre-modifier as used
            usedPres.add(preMod)

        # same for instant modifiers, applied in the end of
        # module cycle
        for postMod in self.postMods:
            if not postMod.type in instantMods:
                continue
            info = postMod.convertToInfo()
            infos.add(info)
            usedPosts.add(postMod)

        # If there're any pre-modifiers which were not used for
        # info generation, mark current effect as partially parsed
        if len(self.preMods.difference(usedPres)) > 0:
            self.effectStatus = InfoBuildStatus.okPartial
        # Same for post-modifiers
        if len(self.postMods.difference(usedPosts)) > 0:
            self.effectStatus = InfoBuildStatus.okPartial

        # Fill context field for all infos
        for info in infos:
            info.requiredContext = infoContext

        # Finally, handle our infos and parsing status to requestor
        return infos, self.effectStatus

    def __builderDurationUnifier(self, modifiers):
        """Unifies similar conditional duration modifiers into single modifier"""
        # Here we will unify duration modifiers which do the same thing,
        # just under different conditions, into single modifier; this is done in order
        # to prevent eos to apply the same modification multiple times.
        # This list holds sets of grouped modifiers
        unifying = []
        # Here we'll add modifiers which are marked for unifying, to avoid checking them
        # again
        grouped = set()
        # Iterate through all combinations of modifiers of 2
        for mod1, mod2 in combinations(modifiers, 2):
            # If both modifiers already were assigned to some group, no point
            # of going further
            if mod1 in grouped and mod2 in grouped:
                continue
            # Skip modifiers which are not the same
            if mod1.isSameMod(mod2) is not True:
                continue
            # If one of the modifiers is already in some modification group, we want to
            # add it there
            if mod1 in grouped or mod2 in grouped:
                # Cycle through unification groups
                for uniGroup in unifying:
                    # Find group with modifier
                    if mod1 in uniGroup or mod2 in uniGroup:
                        # Add our modifiers there and note that we've used both
                        uniGroup.add(mod1)
                        grouped.add(mod1)
                        uniGroup.add(mod2)
                        grouped.add(mod2)
                        break
            # If they're the same, but none of them was grouped already,
            # make new group
            else:
                unifying.append({mod1, mod2})
                grouped.update({mod1, mod2})
        # Go through all groups of modifiers we're going to 'unify'
        for uniGroup in unifying:
            # First, remove them from set of modifiers
            modifiers.difference_update(uniGroup)
            # We need to put something back, 'unified' modification, initialize
            # it to None
            unified = None
            # If there's modification in group without condition, it means
            # that modification will be applied in any case; just mark modifier
            # w/o condition as unified one
            for mod in uniGroup:
                if mod.conditions is None:
                    unified = mod
                    break
            # If unified is still None, then we've got to combine conditions
            if unified is None:
                # Pick random modifier from group, it doesn't matter which one
                unified = uniGroup.pop()
                # For all remaining modifiers
                for mod in uniGroup:
                    # Join conditions of our chosen modifier and picked remaining
                    # modifier using logical OR atoms
                    unifiedCond = Atom()
                    unifiedCond.type = AtomType.logic
                    unifiedCond.operator = AtomLogicOperator.or_
                    unifiedCond.arg1 = unified.conditions
                    unifiedCond.arg2 = mod.conditions
                    unified.conditions = unifiedCond
            # Finally, add unified modifier to set
            modifiers.add(unified)

    def __generic(self, element, conditions):
        """Generic entry point, used if we expect passed element to be meaningful"""
        # For actual modifications, call method which handles them
        if element.operandId in durationMods:
            self.__makeDurationMod(element, conditions)
        elif element.operandId in instantMods:
            self.__makeInstantMod(element, conditions)
        # Mark current effect as partially parsed if it contains
        # inactive operands
        elif element.operandId in inactiveOpnds:
            self.effectStatus = InfoBuildStatus.okPartial
        # Detect if-then-else construct
        elif element.operandId == Operand.or_ and element.arg1 and element.arg1.operandId == Operand.ifThen:
            self.__ifThenElse(element, conditions)
        # Process expressions with other operands using the map
        else:
            genericOpnds = {Operand.splice: self.__splice,
                            Operand.defInt: self.__checkIntStub,
                            Operand.defBool: self.__checkBoolStub}
            genericOpnds[element.operandId](element, conditions)

    def __splice(self, element, conditions):
        """Reference two expressions from self"""
        self.__generic(element.arg1, conditions)
        self.__generic(element.arg2, conditions)

    def __checkIntStub(self, element, conditions):
        """Checks if given expression is stub, returning integer 0 or 1"""
        value = self.__getInt(element)
        if not value in (0, 1):
            raise ValueError("integer stub with unexpected value")

    def __checkBoolStub(self, element, conditions):
        """Checks if given expression is stub, returning boolean true"""
        value = self.__getBool(element)
        if value is not True:
            raise ValueError("boolean stub with value other than True")

    def __makeDurationMod(self, element, conditions):
        """Make modifier for duration expressions"""
        # Make modifier object and let builder know we're working with it
        self.activeMod = Modifier()
        # If we're asked to add any conditions, do it
        if conditions is not None:
            # Make sure to copy whole tree as it may be changed after
            self.activeMod.conditions = deepcopy(conditions)
        # Write modifier type, which corresponds to top-level operand of modification
        self.activeMod.type = element.operandId
        # Request operator and target data, it's always in arg1
        self.__optrTgt(element.arg1)
        # Write down source attribute from arg2
        self.activeMod.sourceType = InfoSourceType.attribute
        self.activeMod.sourceValue = self.__getAttr(element.arg2)
        # Append filled modifier to list we're currently working with
        self.activeSet.add(self.activeMod)
        # If something weird happens, clean current modifier to throw
        # exceptions instead of filling old modifier if something goes wrong
        self.activeMod = None

    def __makeInstantMod(self, element, conditions):
        """Make modifier for instant expressions"""
        # Workflow is almost the same as for duration modifiers
        self.activeMod = Modifier()
        if conditions is not None:
            self.activeMod.conditions = deepcopy(conditions)
        self.activeMod.type = element.operandId
        # As our operator is specified by top-level operand, call target router directly
        self.__tgtRouter(element.arg1)
        self.__srcGetter(element.arg2)
        # Set runtime according to active list
        if self.activeSet is self.preMods:
            self.activeMod.runTime = InfoRunTime.pre
        elif self.activeSet is self.postMods:
            self.activeMod.runTime = InfoRunTime.post
        self.activeSet.add(self.activeMod)
        self.activeMod = None

    def __optrTgt(self, element):
        """Join operator and target definition"""
        # Operation is always in arg1
        self.activeMod.operator = self.__getOptr(element.arg1)
        # Handling of arg2 depends on its operand
        self.__tgtRouter(element.arg2)

    def __tgtRouter(self, element):
        """Pick proper target specifying method according to operand"""
        tgtRouteMap = {Operand.genAttr: self.__tgtAttr,
                       Operand.grpAttr: self.__tgtGrpAttr,
                       Operand.srqAttr: self.__tgtSrqAttr,
                       Operand.itmAttr: self.__tgtItmAttr}
        tgtRouteMap[element.operandId](element)

    def __srcGetter(self, element):
        """Pick proper source specifying method according to operand"""
        # For attribute definitions, store attribute ID as value
        if element.operandId == Operand.defAttr:
            self.activeMod.sourceType = InfoSourceType.attribute
            self.activeMod.sourceValue = self.__getAttr(element)
        # Else, store just direct value
        else:
            valMap = {Operand.defInt: self.__getInt,
                      Operand.defBool: self.__getBool}
            self.activeMod.sourceType = InfoSourceType.value
            self.activeMod.sourceValue = valMap[element.operandId](element)


    def __tgtAttr(self, element):
        """Get target attribute and store it"""
        self.activeMod.targetAttributeId = self.__getAttr(element.arg1)

    def __tgtSrqAttr(self, element):
        """Join target skill requirement and target attribute"""
        self.activeMod.targetSkillRq = self.__getType(element.arg1)
        self.activeMod.targetAttributeId = self.__getAttr(element.arg2)

    def __tgtGrpAttr(self, element):
        """Join target group and target attribute"""
        self.activeMod.targetGroup = self.__getGrp(element.arg1)
        self.activeMod.targetAttributeId = self.__getAttr(element.arg2)

    def __tgtItmAttr(self, element):
        """Join target item specification and target attribute"""
        # Item specification format depends on operand of arg1
        itmGetterMap = {Operand.defLoc: self.__tgtLoc,
                        Operand.locGrp: self.__tgtLocGrp,
                        Operand.locSrq: self.__tgtLocSrq}
        itmGetterMap[element.arg1.operandId](element.arg1)
        # Target attribute is always specified in arg2
        self.activeMod.targetAttributeId = self.__getAttr(element.arg2)

    def __tgtLoc(self, element):
        """Get target location and store it"""
        self.activeMod.targetLocation = self.__getLoc(element)

    def __tgtLocGrp(self, element):
        """Join target location filter and group filter"""
        self.activeMod.targetLocation = self.__getLoc(element.arg1)
        self.activeMod.targetGroup = self.__getGrp(element.arg2)

    def __tgtLocSrq(self, element):
        """Join target location filter and skill requirement filter"""
        self.activeMod.targetLocation = self.__getLoc(element.arg1)
        self.activeMod.targetSkillRq = self.__getType(element.arg2)

    def __getOptr(self, element):
        """Helper for modifying expressions, defines operator"""
        return InfoOperator.expressionValue2operator(element.value)

    def __getLoc(self, element):
        """Define location"""
        return InfoLocation.expressionValue2location(element.value)

    def __getAttr(self, element):
        """Reference attribute via ID"""
        return element.expressionAttributeId

    def __getGrp(self, element):
        """Reference group via ID"""
        return element.expressionGroupId

    def __getType(self, element):
        """Reference type via ID"""
        # Type getter function has special handling
        if element.operandId == Operand.getType:
            # Currently, we have only ID representing self type getter, so run
            # additional check if type getter is for self
            if self.__getLoc(element.arg1) == InfoLocation.self_:
                return Type.self_
            else:
                raise ValueError("unexpected location referenced in type getter")
        else:
            return element.expressionTypeId

    def __getInt(self, element):
        """Get integer from value"""
        return int(element.value)

    def __getBool(self, element):
        """Get integer from value"""
        return bool(element.value)

    def __ifThenElse(self, element, conditions):
        """Handle conditional clause"""
        # Separate passed element into if, then and else clauses,
        # we'll work separately on them
        ifClause = element.arg1.arg1
        thenClause = element.arg1.arg2
        elseClause = element.arg2
        # Get condition data from if clause
        newConditions = self.__makeConditionRouter(ifClause)
        # Combine passed and new conditions into single tree
        currentConditions = self.__appendCondition(conditions, newConditions)
        # Pass copy of conditions to make sure it's not modified there,
        # we'll need them further
        self.__generic(thenClause, deepcopy(currentConditions))
        # Invert condition for else clause processing
        # We do not need to recombine it with conditions passed to our method,
        # as condition being inverted is part of combined tree
        self.__invertCondition(newConditions)
        self.__generic(elseClause, deepcopy(currentConditions))

    def __makeConditionRouter(self, element):
        """Create actual condition node in conditions tree"""
        condRouteMap = {Operand.and_: self.__makeConditionLogic,
                        Operand.or_: self.__makeConditionLogic,
                        Operand.eq: self.__makeConditionComparison,
                        Operand.greater: self.__makeConditionComparison,
                        Operand.greaterEq: self.__makeConditionComparison}
        condition = condRouteMap[element.operandId](element)
        return condition

    def __makeConditionLogic(self, element):
        """Make logic condition node"""
        atomLogicMap = {Operand.and_: AtomLogicOperator.and_,
                        Operand.or_: AtomLogicOperator.or_}
        # Create logic node and fill it
        condLogicAtom = Atom()
        condLogicAtom.type = AtomType.logic
        condLogicAtom.operator = atomLogicMap[element.operandId]
        # Each subnode can be comparison or yet another logical element
        condLogicAtom.arg1 = self.__makeConditionRouter(element.arg1)
        condLogicAtom.arg2 = self.__makeConditionRouter(element.arg2)
        return condLogicAtom

    def __makeConditionComparison(self, element):
        """Make comparison condition node"""
        # Maps expression operands to atom-specific comparison operators
        atomCompMap = {Operand.eq: AtomComparisonOperator.equal,
                       Operand.greater: AtomComparisonOperator.greater,
                       Operand.greaterEq: AtomComparisonOperator.greaterOrEqual}
        # Create comparison node and fill it with data
        condCompAtom = Atom()
        condCompAtom.type = AtomType.comparison
        condCompAtom.operator = atomCompMap[element.operandId]
        condCompAtom.arg1 = self.__conditionPartRouter(element.arg1)
        condCompAtom.arg2 = self.__conditionPartRouter(element.arg2)
        return condCompAtom

    def __conditionPartRouter(self, element):
        """Use proper processing method according to passed operand"""
        condPartMap = {Operand.add: self.__makeCondPartMath,
                       Operand.sub: self.__makeCondPartMath,
                       Operand.itmAttrCond: self.__makeCondPartValRef,
                       Operand.defInt: self.__makeCondPartVal}
        condPartAtom = condPartMap[element.operandId](element)
        return condPartAtom

    def __makeCondPartMath(self, element):
        """Create math condition atom out of expression with mathematical operand"""
        atomMathMap = {Operand.add: AtomMathOperator.add,
                       Operand.sub: AtomMathOperator.subtract}
        conditionMathAtom = Atom()
        conditionMathAtom.type = AtomType.math
        conditionMathAtom.operator = atomMathMap[element.operandId]
        # Each math subnode can be other math node, attribute reference or value,
        # so forward it to router again
        conditionMathAtom.arg1 = self.__conditionPartRouter(element.arg1)
        conditionMathAtom.arg2 = self.__conditionPartRouter(element.arg2)
        return conditionMathAtom

    def __makeCondPartValRef(self, element):
        """Create atom, referring carrier and some attribute on it"""
        valRefAtom = Atom()
        valRefAtom.type = AtomType.valueReference
        valRefAtom.carrier = self.__getLoc(element.arg1)
        valRefAtom.attribute = self.__getAttr(element.arg2)
        return valRefAtom

    def __makeCondPartVal(self, element):
        """Create atom, containing some value within it"""
        argValueMap = {Operand.defInt: self.__getInt}
        valueAtom = Atom()
        valueAtom.type = AtomType.value
        valueAtom.value = argValueMap[element.operandId](element)
        return valueAtom

    def __appendCondition(self, cond1, cond2):
        """Combine two passed condition trees into one"""
        # If any of passed conditions is None, return other one
        if cond1 is None or cond2 is None:
            combined = cond1 or cond2
        # If both exist, combine them using logical and
        else:
            combined = Atom()
            combined.type = AtomType.logic
            combined.operator = AtomLogicOperator.and_
            combined.arg1 = cond1
            combined.arg2 = cond2
        return combined

    def __invertCondition(self, condition):
        """Get negative condition relatively passed condition"""
        # Process logical operands
        if condition.type == AtomType.logic:
            invLogic = {AtomLogicOperator.and_: AtomLogicOperator.or_,
                        AtomLogicOperator.or_: AtomLogicOperator.and_}
            # Replace and with or and vice versa
            condition.operator = invLogic[condition.operator]
            # Request processing of child atoms
            self.__invertCondition(condition.arg1)
            self.__invertCondition(condition.arg2)
        # For comparison atoms, just negate the comparison
        elif condition.type == AtomType.comparison:
            invComps = {AtomComparisonOperator.equal: AtomComparisonOperator.notEqual,
                        AtomComparisonOperator.notEqual: AtomComparisonOperator.equal,
                        AtomComparisonOperator.greater: AtomComparisonOperator.lessOrEqual,
                        AtomComparisonOperator.lessOrEqual: AtomComparisonOperator.greater,
                        AtomComparisonOperator.greaterOrEqual: AtomComparisonOperator.less,
                        AtomComparisonOperator.less: AtomComparisonOperator.greaterOrEqual}
            condition.operator = invComps[condition.operator]
        else:
            raise ValueError("only logical and comparison ConditionAtoms can be reverted")
