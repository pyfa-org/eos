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

from eos.const import RunTime, SourceType
from eos.eve.const import Operand
from eos.exception import ModifierBuilderException, ConditionBuilderException
from .conditionBuilder import ConditionBuilder
from .helpers import ExpressionData, operandData, OperandType
from .modifier import Modifier


class ModifierBuilder:
    """
    Class is responsible for converting two trees (pre and post) of Expression objects (which
    aren't directly useful to us) into Modifier objects.
    """

    def build(self, expressionTree, treeRunTime, effectCategoryId):
        """
        Generate Modifier objects out of passed data.

        Positional arguments:
        expressionTree -- root expression of expression tree
        treeRunTime -- is it pre- or post-expression tree, used
        to define type of instant modifiers, must be RunTime.pre
        or RunTime.post
        effectCategoryId -- effect category ID of effect, whose
        expression Tree we're going to parse

        Return value:
        Tuple (set with Modifier objects, skipped data flag), where
        skipped data flag indicates that we have encountered inactive
        operands
        """
        # Flag which indicates, did we have data which we
        # are skipping or not
        self.skippedData = False
        # Set with already generated modifiers
        self.modifiers = set()
        # Variable keeping type of tree we're parsing (pre
        # or post)
        self.treeRunTime = treeRunTime
        # Which modifier we're building, used during build
        # process for convenience
        self.activeModifier = None
        # Conditions applied to all expressions found on current
        # building stage
        self.conditions = None
        # Run parsing process
        self.__generic(expressionTree, None)
        # Unify multiple modifiers which do the same thing, but under different
        # conditions, into single modifiers. We need this for pre-modifiers only,
        # as post-modifiers shouldn't contain conditions by definition, if they
        # do - they will be invalidated later
        if treeRunTime == RunTime.pre:
            self.__builderDurationUnifier()
        # Set effectCategoryId attribute for all modifiers
        for modifier in self.modifiers:
            modifier.effectCategoryId = effectCategoryId
        return self.modifiers, self.skippedData

    def __generic(self, element, conditions):
        """Generic entry point, used if we expect passed element to be meaningful"""
        try:
            operandMeta = operandData[element.operandId]
        except KeyError:
            operandType = None
        else:
            operandType = operandMeta.type
        # For actual modifications, call method which handles them
        if operandType == OperandType.duration:
            self.__makeDurationMod(element, conditions)
        elif operandType == OperandType.instant:
            self.__makeInstantMod(element, conditions)
        # Mark current effect as partially parsed if it contains
        # inactive operands
        elif operandType == OperandType.inactive:
            self.skippedData = True
        # Detect if-then-else construct
        elif element.operandId == Operand.or_ and element.arg1 and element.arg1.operandId == Operand.ifThen:
            self.__ifThenElse(element, conditions)
        # Process expressions with other operands using the map
        else:
            genericOpnds = {Operand.splice: self.__splice,
                            Operand.defInt: self.__checkIntStub,
                            Operand.defBool: self.__checkBoolStub}
            try:
                method = genericOpnds[element.operandId]
            except KeyError as e:
                raise ModifierBuilderException("unknown operand has been passed to __generic") from e
            method(element, conditions)

    def __splice(self, element, conditions):
        """Reference two expressions from self"""
        self.__generic(element.arg1, conditions)
        self.__generic(element.arg2, conditions)

    def __checkIntStub(self, element, conditions):
        """Checks if given expression is stub, returning integer 0 or 1"""
        value = ExpressionData.getInteger(element)
        if not value in {0, 1}:
            raise ModifierBuilderException("integer stub with unexpected value")

    def __checkBoolStub(self, element, conditions):
        """Checks if given expression is stub, returning boolean true"""
        value = ExpressionData.getBoolean(element)
        if value is not True:
            raise ModifierBuilderException("boolean stub with value other than True")

    def __makeDurationMod(self, element, conditions):
        """Make modifier for duration expressions"""
        # Make modifier object and let builder know we're working with it
        self.activeModifier = Modifier()
        # If we're asked to add any conditions, do it
        if conditions is not None:
            # Make sure to copy whole tree as it may be changed after
            self.activeModifier.conditions = deepcopy(conditions)
        # Write modifier type, which corresponds to top-level operand of modification
        self.activeModifier.type = element.operandId
        # Request operator and target data, it's always in arg1
        self.__optrTgt(element.arg1)
        # Write down source attribute from arg2
        self.activeModifier.sourceType = SourceType.attribute
        self.activeModifier.sourceValue = ExpressionData.getAttribute(element.arg2)
        # Append filled modifier to list we're currently working with
        self.modifiers.add(self.activeModifier)
        # If something weird happens, clean current modifier to throw
        # exceptions instead of filling old modifier if something goes wrong
        self.activeModifier = None

    def __makeInstantMod(self, element, conditions):
        """Make modifier for instant expressions"""
        # Workflow is almost the same as for duration modifiers
        self.activeModifier = Modifier()
        if conditions is not None:
            self.activeModifier.conditions = deepcopy(conditions)
        self.activeModifier.type = element.operandId
        # As our operator is specified by top-level operand, call target router directly
        self.__tgtRouter(element.arg1)
        self.__srcGetter(element.arg2)
        # Set runtime of modifier according to data
        # passed to builder
        self.activeModifier.runTime = self.treeRunTime
        self.modifiers.add(self.activeModifier)
        self.activeModifier = None

    def __optrTgt(self, element):
        """Join operator and target definition"""
        # Operation is always in arg1
        self.activeModifier.operator = ExpressionData.getOperator(element.arg1)
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
            self.activeModifier.sourceType = SourceType.attribute
            self.activeModifier.sourceValue = ExpressionData.getAttribute(element)
        # Else, store just direct value
        else:
            valMap = {Operand.defInt: ExpressionData.getInteger,
                      Operand.defBool: ExpressionData.getBoolean}
            self.activeModifier.sourceType = SourceType.value
            self.activeModifier.sourceValue = valMap[element.operandId](element)

    def __tgtAttr(self, element):
        """Get target attribute and store it"""
        self.activeModifier.targetAttributeId = ExpressionData.getAttribute(element.arg1)

    def __tgtSrqAttr(self, element):
        """Join target skill requirement and target attribute"""
        self.activeModifier.targetSkillRequirementId = ExpressionData.getType(element.arg1)
        self.activeModifier.targetAttributeId = ExpressionData.getAttribute(element.arg2)

    def __tgtGrpAttr(self, element):
        """Join target group and target attribute"""
        self.activeModifier.targetGroupId = ExpressionData.getGroup(element.arg1)
        self.activeModifier.targetAttributeId = ExpressionData.getAttribute(element.arg2)

    def __tgtItmAttr(self, element):
        """Join target item specification and target attribute"""
        # Item specification format depends on operand of arg1
        itmGetterMap = {Operand.defLoc: self.__tgtLoc,
                        Operand.locGrp: self.__tgtLocGrp,
                        Operand.locSrq: self.__tgtLocSrq}
        itmGetterMap[element.arg1.operandId](element.arg1)
        # Target attribute is always specified in arg2
        self.activeModifier.targetAttributeId = ExpressionData.getAttribute(element.arg2)

    def __tgtLoc(self, element):
        """Get target location and store it"""
        self.activeModifier.targetLocation = ExpressionData.getLocation(element)

    def __tgtLocGrp(self, element):
        """Join target location filter and group filter"""
        self.activeModifier.targetLocation = ExpressionData.getLocation(element.arg1)
        self.activeModifier.targetGroupId = ExpressionData.getGroup(element.arg2)

    def __tgtLocSrq(self, element):
        """Join target location filter and skill requirement filter"""
        self.activeModifier.targetLocation = ExpressionData.getLocation(element.arg1)
        self.activeModifier.targetSkillRequirementId = ExpressionData.getType(element.arg2)

    def __ifThenElse(self, element, conditions):
        """Handle conditional clause"""
        # Separate passed element into if, then and else clauses,
        # we'll work separately on them
        ifClause = element.arg1.arg1
        thenClause = element.arg1.arg2
        elseClause = element.arg2
        # Get condition data from if clause
        newConditions = ConditionBuilder.build(ifClause)
        # Combine passed and new conditions into single tree
        currentConditions = ConditionBuilder.conjuct(conditions, newConditions)
        # Pass copy of conditions to make sure it's not modified there,
        # we'll need them further
        self.__generic(thenClause, deepcopy(currentConditions))
        # Invert condition for else clause processing
        # We do not need to recombine it with conditions passed to our method,
        # as condition being inverted is part of combined tree
        try:
            ConditionBuilder.invert(newConditions)
        except ConditionBuilderException as e:
            raise ModifierBuilderException("failed to invert condition") from e
        self.__generic(elseClause, deepcopy(currentConditions))

    def __builderDurationUnifier(self):
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
        for mod1, mod2 in combinations(self.modifiers, 2):
            # If both modifiers already were assigned to some group, no point
            # of going further
            if mod1 in grouped and mod2 in grouped:
                continue
            # Skip modifiers which are not the same
            if self.__isSameMod(mod1, mod2) is not True:
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
            self.modifiers.difference_update(uniGroup)
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
                    # Disjunct conditions
                    unified.conditions = ConditionBuilder.disjunct(unified.conditions, mod.conditions)
            # Finally, add unified modifier to set
            self.modifiers.add(unified)

    def __isSameMod(self, mod1, mod2):
        """
        Check if both duration modifiers actually do the same thing

        Positional arguments:
        mod1 -- first modifier to check
        mod2 -- second modifier to check

        Return value:
        True if both modifiers are duration and all their duration-related
        attributes are the same, else False
        """
        # Check if both are duration modifiers
        for modifier in {mod1, mod2}:
            try:
                modData = operandData[modifier.type]
            except KeyError:
                modType = None
            else:
                modType = modData.type
            if modType != OperandType.duration:
                return False
        # Check all modifier fields that make the difference for duration modifiers
        if (mod1.type != mod2.type or mod1.effectCategoryId != mod2.effectCategoryId or
            mod1.sourceType != mod2.sourceType or mod1.sourceValue != mod2.sourceValue or
            mod1.operator != mod2.operator or mod1.targetAttributeId != mod2.targetAttributeId or
            mod1.targetLocation != mod2.targetLocation or mod1.targetGroupId != mod2.targetGroupId or
            mod1.targetSkillRequirementId != mod2.targetSkillRequirementId):
            return False
        # They're the same if above conditions were passed, other fields irrelevant
        return True
