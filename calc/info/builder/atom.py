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


class AtomType:
    """Condition atom type ID holder"""
    logic = 1  # Logical OR or AND
    comparison = 2  # Comparison of arguments
    math = 3  # Some math operation applied onto arguments
    valueReference = 4  # Reference to attribute value
    value = 5  # Value is enclosed in atom itself


class AtomLogicOperator:
    """Condition atom logical operator ID holder"""
    and_ = 1  # Logical and
    or_ = 2  # Logical or


class AtomComparisonOperator:
    """Condition atom comparison operator ID holder"""
    equal = 1  # ==
    notEqual = 2  # !=
    less = 3  # <
    lessOrEqual = 4  # <=
    greater = 5  # >
    greaterOrEqual = 6  # >=


class AtomMathOperator:
    """Condition atom math operator ID holder"""
    add = 1  # +
    subtract = 2  # -


class Atom:
    """Stores bit of Info condition metadata"""

    def __init__(self):
        # Describes purpose of this atom.
        # Must take any atomType* value from const file.
        self.type = None

        # For some atom types, describes which operator should be applied onto its arguments.
        # For atomTypeLogic, holds atomLogic* from const file.
        # For atomTypeComp, holds atomComp* from const file.
        # For atomTypeMath, holds atomMath* from const file.
        self.operator = None

        # For all types besides atomTypeVal, contains reference to child atom.
        self.arg1 = None

        # For all types besides atomTypeVal, contains reference to child atom.
        self.arg2 = None

        # For atomTypeValRef, contains reference to some location.
        self.carrier = None

        # For atomTypeValRef, contains reference to attribute in some location.
        self.attribute = None

        # For atomTypeVal, contains pre-stored atom value.
        self.value = None

    def __repr__(self, indent=""):
        """Convert atom tree, starting from self, to string"""
        # Scatter logic operator and its arguments into several lines with different
        # indentation level
        if self.type == AtomType.logic:
            logicLiterals = {AtomLogicOperator.and_: "and",
                             AtomLogicOperator.or_: "or"}
            newindent = "  {0}".format(indent)
            result = "{2}\n{0}{1}\n{3}".format(indent, logicLiterals[self.operator], self.arg1.__repr__(indent=newindent), self.arg2.__repr__(indent=newindent))
        # Print comparison on the same line with its arguments, just place them in brackets
        elif self.type == AtomType.comparison:
            compLiterals = {AtomComparisonOperator.equal: "==",
                            AtomComparisonOperator.notEqual: "!=",
                            AtomComparisonOperator.less: "<",
                            AtomComparisonOperator.lessOrEqual: "<=",
                            AtomComparisonOperator.greater: ">",
                            AtomComparisonOperator.greaterOrEqual: ">="}
            newindent = "  {0}".format(indent)
            result = "{0}({2}) {1} ({3})".format(indent, compLiterals[self.operator], self.arg1.__repr__(), self.arg2.__repr__())
        # Math operations are printed on the same line with its arguments
        elif self.type == AtomType.math:
            mathLiterals = {AtomMathOperator.add: "+",
                            AtomMathOperator.subtract: "-"}
            newindent = "  {0}".format(indent)
            result = "{0}{2} {1} {3}".format(indent, mathLiterals[self.operator], self.arg1.__repr__(), self.arg2.__repr__())
        # Tag carrier location with c, its attribute with a
        elif self.type == AtomType.valueReference:
            result = "c{0}.a{1}".format(self.carrier, self.attribute)
        # Print hardcoded values with v tag
        elif self.type == AtomType.value:
            result = "v{0}".format(self.value)
        return result

    def validateTree(self):
        """Validate full condition tree, given we're checking top-level node"""
        # Top-level node can be either logical join or comparison
        allowedTypes = {AtomType.logic, AtomType.comparison}
        if not self.type in allowedTypes:
            return False
        return self.__validateNode()

    def __validateNode(self):
        """Validates object fields"""
        validationRouter = {AtomType.logic: self.__valLogic,
                            AtomType.comparison: self.__valComp,
                            AtomType.math: self.__valMath,
                            AtomType.valueReference: self.__valValRef,
                            AtomType.value: self.__valVal}
        try:
            method = validationRouter[self.type]
        except KeyError:
            return False
        return method()

    def __valLogic(self):
        if self.carrier is not None or self.attribute is not None or \
        self.value is not None:
            return False
        allowedSubtypes = {AtomType.logic, AtomType.comparison}
        try:
            if not self.arg1.type in allowedSubtypes or not self.arg2.type in allowedSubtypes:
                return False
        except AttributeError:
            return False
        if self.arg1.__validateNode() is not True or self.arg2.__validateNode() is not True:
            return False
        return True

    def __valComp(self):
        if self.carrier is not None or self.attribute is not None or \
        self.value is not None:
            return False
        allowedSubtypes = {AtomType.math, AtomType.valueReference, AtomType.value}
        try:
            if not self.arg1.type in allowedSubtypes or not self.arg2.type in allowedSubtypes:
                return False
        except AttributeError:
            return False
        if self.arg1.__validateNode() is not True or self.arg2.__validateNode() is not True:
            return False
        return True

    def __valMath(self):
        if self.carrier is not None or self.attribute is not None or \
        self.value is not None:
            return False
        allowedSubtypes = {AtomType.math, AtomType.valueReference, AtomType.value}
        try:
            if not self.arg1.type in allowedSubtypes or not self.arg2.type in allowedSubtypes:
                return False
        except AttributeError:
            return False
        if self.arg1.__validateNode() is not True or self.arg2.__validateNode() is not True:
            return False
        return True

    def __valValRef(self):
        if self.arg1 is not None or self.arg2 is not None or \
        self.value is not None:
            return False
        if self.carrier is None or self.attribute is None:
            return False
        return True

    def __valVal(self):
        if self.arg1 is not None or self.arg2 is not None or \
        self.carrier is not None or self.attribute is not None:
            return False
        if self.value is None:
            return False
        return True
