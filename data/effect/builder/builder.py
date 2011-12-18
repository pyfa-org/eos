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

from copy import deepcopy

from eos import const
from .atom import ConditionAtom
from .modifier import Modifier
from .localData import durationMods, instantMods

# Operands which are not used in any way in current Eos implementation
inactiveOpnds = {const.opndEcmBurst, const.opndAoeDmg, const.opndShipScan,
                 const.opndSurveyScan, const.opndCargoScan, const.opndPowerBooster,
                 const.opndAoeDecloak, const.opndTgtHostile, const.opndTgtSilent,
                 const.opndCheatTeleDock, const.opndCheatTeleGate, const.opndAttack,
                 const.opndMissileLaunch, const.opndVrfTgtGrp, const.opndToolTgtSkills,
                 const.opndMine, const.opndDefenderLaunch, const.opndFofLaunch,
                 const.opndUserError}

class InfoBuilder(object):
    """
    EffectInfo is responsible for converting two trees (pre and post) of Expression objects (which
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

    def build(self, preExpression, postExpression):
        """
        Go through both trees and compose our EffectInfos
        """
        self.activeSet = self.preMods
        try:
            self.__generic(preExpression, None)
        except:
            print("Error building pre-expression tree with base {}".format(preExpression.id))
            return set()
        for mod in self.preMods:
            if mod.validate() is not True:
                print("Error validating pre-modifiers of base {}".format(preExpression.id))
                return set()

        self.activeSet = self.postMods
        try:
            self.__generic(postExpression, None)
        except:
            print("Error building post-expression tree with base {}".format(postExpression.id))
            return set()
        for mod in self.postMods:
            if mod.validate() is not True:
                print("Error validating post-modifiers of base {}".format(postExpression.id))
                return set()
        infos = set()
        usedPres = set()
        usedPosts = set()

        for preMod in self.preMods:
            if not preMod.type in durationMods:
                continue
            for postMod in self.postMods:
                if postMod in usedPosts:
                    continue
                if preMod.isMirror(postMod) is True:
                    info = preMod.convertToInfo()
                    infos.add(info)
                    usedPres.add(preMod)
                    usedPosts.add(postMod)
                    break

        for preMod in self.preMods:
            if not preMod.type in instantMods:
                continue
            if preMod in usedPres:
                continue
            info = preMod.convertToInfo()
            infos.add(info)
            usedPres.add(preMod)

        for postMod in self.postMods:
            if not postMod.type in instantMods:
                continue
            if postMod in usedPosts:
                continue
            info = postMod.convertToInfo()
            infos.add(info)
            usedPosts.add(postMod)

        for preMod in self.preMods:
            if not preMod in usedPres:
                print("Warning: unused pre-expression modifier in base {}".format(preExpression.id))
                break
        for postMod in self.postMods:
            if not postMod in usedPosts:
                print("Warning: unused post-expression modifier in base {}".format(postExpression.id))
                break

        return infos

    def __generic(self, element, conditions):
        """Generic entry point, used if we expect passed element to be meaningful"""
        # For actual modifications, call method which handles them
        if element.operand in durationMods:
            self.__makeDurationMod(element, conditions)
        elif element.operand in instantMods:
            self.__makeInstantMod(element, conditions)
        # Do nothing for inactive operands
        elif element.operand in inactiveOpnds:
            pass
        elif element.operand == const.opndOr:
            self.__ifThenElse(element, conditions)
        # Process expressions with other operands using the map
        else:
            genericOpnds = {const.opndSplice: self.__splice,
                            const.opndDefInt: self.__checkIntStub,
                            const.opndDefBool: self.__checkBoolStub}
            genericOpnds[element.operand](element, conditions)

    def __splice(self, element, conditions):
        """Reference two expressions from self"""
        self.__generic(element.arg1, conditions)
        self.__generic(element.arg2, conditions)

    def __checkIntStub(self, element, conditions):
        """Checks if given expression is stub, returning integer 1"""
        value = self.__getInt(element)
        if value != 1:
            raise ValueError("integer stub with value other than 1")

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
        self.activeMod.type = element.operand
        # Request operator and target data, it's always in arg1
        self.__optrTgt(element.arg1)
        # Write down source attribute from arg2
        self.activeMod.sourceAttribute = self.__getAttr(element.arg2)
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
        self.activeMod.type = element.operand
        # As our operation is specified by top-level operand, call target router directly
        self.__tgtRouter(element.arg1)
        self.activeMod.sourceAttribute = self.__getAttr(element.arg2)
        # Set runtime according to active list
        if self.activeSet is self.preMods:
            self.activeMod.runTime = const.infoPre
        elif self.activeSet is self.postMods:
            self.activeMod.runTime = const.infoPost
        self.activeSet.add(self.activeMod)
        self.activeMod = None

    def __optrTgt(self, element):
        """Join operator and target definition"""
        # Operation is always in arg1
        self.activeMod.operation = self.__getOptr(element.arg1)
        # Handling of arg2 depends on its operand
        self.__tgtRouter(element.arg2)

    def __tgtRouter(self, element):
        """Pick proper target specifying method according to operand"""
        tgtRouteMap = {const.opndGenAttr: self.__tgtAttr,
                       const.opndGrpAttr: self.__tgtGrpAttr,
                       const.opndSrqAttr: self.__tgtSrqAttr,
                       const.opndItmAttr: self.__tgtItmAttr}
        tgtRouteMap[element.operand](element)

    def __tgtAttr(self, element):
        """Get target attribute and store it"""
        self.activeMod.targetAttribute = self.__getAttr(element.arg1)

    def __tgtSrqAttr(self, element):
        """Join target skill requirement and target attribute"""
        self.activeMod.targetSkillRq = self.__getType(element.arg1)
        self.activeMod.targetAttribute = self.__getAttr(element.arg2)

    def __tgtGrpAttr(self, element):
        """Join target group and target attribute"""
        self.activeMod.targetGroup = self.__getGrp(element.arg1)
        self.activeMod.targetAttribute = self.__getAttr(element.arg2)

    def __tgtItmAttr(self, element):
        """Join target item specification and target attribute"""
        # Item specification format depends on operand of arg1
        itmGetterMap = {const.opndDefLoc: self.__tgtLoc,
                        const.opndLocGrp: self.__tgtLocGrp,
                        const.opndLocSrq: self.__tgtLocSrq}
        itmGetterMap[element.arg1.operand](element.arg1)
        # Target attribute is always specified in arg2
        self.activeMod.targetAttribute = self.__getAttr(element.arg2)

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
        return const.optrConvMap[element.value]

    def __getLoc(self, element):
        """Define location"""
        return const.locConvMap[element.value]

    def __getAttr(self, element):
        """Reference attribute via ID"""
        return element.attributeId

    def __getGrp(self, element):
        """Reference group via ID"""
        return element.groupId

    def __getType(self, element):
        """Reference type via ID"""
        # Type getter function has special handling
        if element.operand == const.opndGetType:
            # Currently, we have only ID representing self type getter, so run
            # additional check if type getter is for self
            if self.__getLoc(element.arg1) == const.locSelf:
                return const.selfTypeID
            else:
                raise ValueError("unexpected location referenced in type getter")
        else:
            return element.typeId

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
        newConditions = self.__makeCondition(ifClause)
        # Combine passed and new conditions into single tree
        currentConditions = self.__appendCondition(conditions, newConditions)
        # Pass copy of conditions to make sure it's not modified there,
        # we'll need them further
        self.__generic(thenClause, deepcopy(currentConditions))
        # To get proper condition tree for modifiers contained in else clause, we need
        # to invert comparison operator of new condition set
        invConds = {const.atomCompEq: const.atomCompNotEq,
                    const.atomCompGreat: const.atomCompLessEq,
                    const.atomCompGreatEq: const.atomCompLess}
        # As it's written directly to tree which is in combined set too, we do not
        # need to make combined tree again
        newConditions.operator = invConds[newConditions.operator]
        self.__generic(elseClause, deepcopy(currentConditions))

    def __makeCondition(self, element):
        """Create actual condition node in conditions tree"""
        # Maps expression operands to atom-specific comparison operations
        condOpndAtomMap = {const.opndEq: const.atomCompEq,
                           const.opndGreater: const.atomCompGreat,
                           const.opndGreaterEq: const.atomCompGreatEq}
        # Create condition node and fill it with data
        if element.operand in condOpndAtomMap:
            conditionTopAtom = ConditionAtom()
            conditionTopAtom.type = const.atomTypeComp
            conditionTopAtom.operator = condOpndAtomMap[element.operand]
            conditionTopAtom.arg1 = self.__getAtomCompArg(element.arg1)
            conditionTopAtom.arg2 = self.__getAtomCompArg(element.arg2)
            return conditionTopAtom
        else:
            raise ValueError("unknown operand in expression passed as condition")

    def __appendCondition(self, cond1, cond2):
        """Combine two passed condition trees into one"""
        # If any of passed conditions is None, return other one
        if cond1 is None or cond2 is None:
            combined = cond1 or cond2
        # If both exist, combine them using logical and
        else:
            combined = ConditionAtom()
            combined.type = const.atomTypeLogic
            combined.operator = const.atomLogicAnd
            combined.arg1 = cond1
            combined.arg2 = cond2
        return combined

    def __getAtomCompArg(self, element):
        """Get comparison argument atom tree"""
        # Create atom for location.attribute references
        if element.operand == const.opndItmAttrCond:
            attrAtom = ConditionAtom()
            attrAtom.type = const.atomTypeValRef
            attrAtom.carrier = self.__getLoc(element.arg1)
            attrAtom.attribute = self.__getAttr(element.arg2)
            return attrAtom
        # Create atom for plain value specifications
        argValueMap = {const.opndDefInt: self.__getInt}
        if element.operand in argValueMap:
            valueAtom = ConditionAtom()
            valueAtom.type = const.atomTypeVal
            valueAtom.value = argValueMap[element.operand](element)
            return valueAtom
        raise ValueError("unknown operand in expression passed as comparison part")
