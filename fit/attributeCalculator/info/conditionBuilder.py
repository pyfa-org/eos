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


from eos.const import AtomType, AtomLogicOperator, AtomComparisonOperator, AtomMathOperator
from eos.eve.const import Operand
from .condition import Atom
from .exception import ConditionBuilderException
from .helpers import ExpressionData


class ConditionBuilder:
    """
    Class is responsible for converting expression tree into tree of
    Atom objects, which represent condition data, and for various
    operations performed upon it.
    """

    @classmethod
    def build(cls, expression):
        """Create actual condition node in conditions tree"""
        condRouteMap = {Operand.and_: cls.__makeConditionLogic,
                        Operand.or_: cls.__makeConditionLogic,
                        Operand.eq: cls.__makeConditionComparison,
                        Operand.greater: cls.__makeConditionComparison,
                        Operand.greaterEq: cls.__makeConditionComparison}
        condition = condRouteMap[expression.operandId](expression)
        return condition

    @classmethod
    def __makeConditionLogic(cls, element):
        """Make logic condition node"""
        atomLogicMap = {Operand.and_: AtomLogicOperator.and_,
                        Operand.or_: AtomLogicOperator.or_}
        # Create logic node and fill it
        condLogicAtom = Atom()
        condLogicAtom.type = AtomType.logic
        condLogicAtom.operator = atomLogicMap[element.operandId]
        # Each subnode can be comparison or yet another logical element
        condLogicAtom.child1 = cls.build(element.arg1)
        condLogicAtom.child2 = cls.build(element.arg2)
        return condLogicAtom

    @classmethod
    def __makeConditionComparison(cls, element):
        """Make comparison condition node"""
        # Maps expression operands to atom-specific comparison operators
        atomCompMap = {Operand.eq: AtomComparisonOperator.equal,
                       Operand.greater: AtomComparisonOperator.greater,
                       Operand.greaterEq: AtomComparisonOperator.greaterOrEqual}
        # Create comparison node and fill it with data
        condCompAtom = Atom()
        condCompAtom.type = AtomType.comparison
        condCompAtom.operator = atomCompMap[element.operandId]
        condCompAtom.child1 = cls.__conditionPartRouter(element.arg1)
        condCompAtom.child2 = cls.__conditionPartRouter(element.arg2)
        return condCompAtom

    @classmethod
    def __conditionPartRouter(cls, element):
        """Use proper processing method according to passed operand"""
        condPartMap = {Operand.add: cls.__makeCondPartMath,
                       Operand.sub: cls.__makeCondPartMath,
                       Operand.itmAttrCond: cls.__makeCondPartValRef,
                       Operand.defInt: cls.__makeCondPartVal}
        condPartAtom = condPartMap[element.operandId](element)
        return condPartAtom

    @classmethod
    def __makeCondPartMath(cls, element):
        """Create math condition atom out of expression with mathematical operand"""
        atomMathMap = {Operand.add: AtomMathOperator.add,
                       Operand.sub: AtomMathOperator.subtract}
        conditionMathAtom = Atom()
        conditionMathAtom.type = AtomType.math
        conditionMathAtom.operator = atomMathMap[element.operandId]
        # Each math subnode can be other math node, attribute reference or value,
        # so forward it to router again
        conditionMathAtom.child1 = cls.__conditionPartRouter(element.arg1)
        conditionMathAtom.child2 = cls.__conditionPartRouter(element.arg2)
        return conditionMathAtom

    @classmethod
    def __makeCondPartValRef(cls, element):
        """Create atom, referring carrier and some attribute on it"""
        valRefAtom = Atom()
        valRefAtom.type = AtomType.valueReference
        valRefAtom.carrier = ExpressionData.getLocation(element.arg1)
        valRefAtom.attribute = ExpressionData.getAttribute(element.arg2)
        return valRefAtom

    @classmethod
    def __makeCondPartVal(cls, element):
        """Create atom, containing some value within it"""
        argValueMap = {Operand.defInt: ExpressionData.getInteger}
        valueAtom = Atom()
        valueAtom.type = AtomType.value
        valueAtom.value = argValueMap[element.operandId](element)
        return valueAtom

    @classmethod
    def invert(cls, condition):
        """Invert passed condition"""
        # Process logical operands
        if condition.type == AtomType.logic:
            invLogic = {AtomLogicOperator.and_: AtomLogicOperator.or_,
                        AtomLogicOperator.or_: AtomLogicOperator.and_}
            # Replace and with or and vice versa
            condition.operator = invLogic[condition.operator]
            # Request processing of child atoms
            cls.invert(condition.child1)
            cls.invert(condition.child2)
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
            raise ConditionBuilderException("only logical and comparison ConditionAtoms can be inverted")

    @classmethod
    def conjuct(cls, cond1, cond2):
        """Conjuct two passed condition trees"""
        # If any of passed conditions is None, return other one
        if cond1 is None or cond2 is None:
            combined = cond1 or cond2
        # If both exist, combine them using logical and
        else:
            combined = Atom()
            combined.type = AtomType.logic
            combined.operator = AtomLogicOperator.and_
            combined.child1 = cond1
            combined.child2 = cond2
        return combined

    @classmethod
    def disjunct(cls, cond1, cond2):
        """Disjunct two passed condition trees"""
        # If any of passed conditions is None, return other one
        if cond1 is None or cond2 is None:
            combined = cond1 or cond2
        # If both exist, combine them using logical and
        else:
            combined = Atom()
            combined.type = AtomType.logic
            combined.operator = AtomLogicOperator.or_
            combined.child1 = cond1
            combined.child2 = cond2
        return combined
