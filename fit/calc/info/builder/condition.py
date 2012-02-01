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


class Atom:
    """Stores bit of Info condition metadata"""

    def __init__(self):
        # Describes purpose of this atom, must be AtomType
        # class' attribute value
        self.type = None
        # Which operator should be applied to combine its childs:
        # For type.logic, must be AtomLogicOperator class' attribute value;
        # For type.comparison, must be AtomComparisonOperator class' attribute value;
        # For type.math, must be AtomMathOperator class' attribute value;
        # For other atom types, must be None.
        self.operator = None

        # Contains reference to child atom:
        # For type.value, must be None;
        # For other atom types, must refer child Atom.
        self.child1 = None
        self.child2 = None

        # Contains reference to some location:
        # For type.valueReference, must be InfoLocation class' attribute value;
        # For other atom types, must be None.
        self.carrier = None

        # Contains reference to some attribute:
        # For type.valueReference, must be integer which refers attribute via ID;
        # For other atom types, must be None.
        self.attribute = None

        # Contains value, which is used as element in math or comparison operations:
        # For type.value, contains value;
        # For other atom types, must be None.
        self.value = None

    def __repr__(self, indent=""):
        """Convert atom tree to pretty string, starting from self"""
        # Scatter logic operator and its arguments into several lines with different
        # indentation level
        if self.type == AtomType.logic:
            logicLiterals = {AtomLogicOperator.and_: "and",
                             AtomLogicOperator.or_: "or"}
            newindent = "  {0}".format(indent)
            result = "{2}\n{0}{1}\n{3}".format(indent, logicLiterals[self.operator], self.child1.__repr__(indent=newindent), self.child2.__repr__(indent=newindent))
        # Print comparison on the same line with its arguments, just place them in brackets
        elif self.type == AtomType.comparison:
            compLiterals = {AtomComparisonOperator.equal: "==",
                            AtomComparisonOperator.notEqual: "!=",
                            AtomComparisonOperator.less: "<",
                            AtomComparisonOperator.lessOrEqual: "<=",
                            AtomComparisonOperator.greater: ">",
                            AtomComparisonOperator.greaterOrEqual: ">="}
            newindent = "  {0}".format(indent)
            result = "{0}({2}) {1} ({3})".format(indent, compLiterals[self.operator], self.child1.__repr__(), self.child2.__repr__())
        # Math operations are printed on the same line with its arguments
        elif self.type == AtomType.math:
            mathLiterals = {AtomMathOperator.add: "+",
                            AtomMathOperator.subtract: "-"}
            newindent = "  {0}".format(indent)
            result = "{0}{2} {1} {3}".format(indent, mathLiterals[self.operator], self.child1.__repr__(), self.child2.__repr__())
        # Tag carrier location with c, its attribute with a
        elif self.type == AtomType.valueReference:
            result = "c{0}.a{1}".format(self.carrier, self.attribute)
        # Print hardcoded values with v tag
        elif self.type == AtomType.value:
            result = "v{0}".format(self.value)
        return result

    def validateTree(self):
        """
        Validate full condition tree, given we're checking top-level node.

        Return value:
        True if tree is valid, False if tree is not valid
        """
        # Top-level node can be either logical join or comparison
        allowedTypes = {AtomType.logic, AtomType.comparison}
        if not self.type in allowedTypes:
            return False
        return self.__validateNode()

    def __validateNode(self):
        """
        Pick appropriate validation method and run it.

        Return value:
        False if no proper method has been picked, else
        transmit value returned by ran method
        """
        validationRouter = {AtomType.logic: self.__validateLogic,
                            AtomType.comparison: self.__validateComparison,
                            AtomType.math: self.__validateMath,
                            AtomType.valueReference: self.__validateValueReference,
                            AtomType.value: self.__validateValue}
        try:
            method = validationRouter[self.type]
        except KeyError:
            return False
        return method()

    def __validateLogic(self):
        if (self.carrier is not None or self.attribute is not None or
            self.value is not None):
            return False
        allowedSubtypes = {AtomType.logic, AtomType.comparison}
        try:
            if not self.child1.type in allowedSubtypes or not self.child2.type in allowedSubtypes:
                return False
        except AttributeError:
            return False
        if self.child1.__validateNode() is not True or self.child2.__validateNode() is not True:
            return False
        return True

    def __validateComparison(self):
        if (self.carrier is not None or self.attribute is not None or
            self.value is not None):
            return False
        allowedSubtypes = {AtomType.math, AtomType.valueReference, AtomType.value}
        try:
            if not self.child1.type in allowedSubtypes or not self.child2.type in allowedSubtypes:
                return False
        except AttributeError:
            return False
        if self.child1.__validateNode() is not True or self.child2.__validateNode() is not True:
            return False
        return True

    def __validateMath(self):
        if (self.carrier is not None or self.attribute is not None or
            self.value is not None):
            return False
        allowedSubtypes = {AtomType.math, AtomType.valueReference, AtomType.value}
        try:
            if not self.child1.type in allowedSubtypes or not self.child2.type in allowedSubtypes:
                return False
        except AttributeError:
            return False
        if self.child1.__validateNode() is not True or self.child2.__validateNode() is not True:
            return False
        return True

    def __validateValueReference(self):
        if (self.child1 is not None or self.child2 is not None or
            self.value is not None):
            return False
        if self.carrier is None or self.attribute is None:
            return False
        return True

    def __validateValue(self):
        if (self.child1 is not None or self.child2 is not None or
            self.carrier is not None or self.attribute is not None):
            return False
        if self.value is None:
            return False
        return True
