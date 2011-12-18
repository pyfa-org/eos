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

from eos import const

class ConditionAtom(object):
    """
    Stores bit of Info condition metadata
    """
    def __init__(self):
        self.type = None
        """
        Describes purpose of this atom.
        Must take any atomType* value from consts.
        """

        self.operator = None
        """
        For some atom types, describes which operation should be applied onto its arguments.
        For atomTypeLogic, holds atomLogic* from const file.
        For atomTypeComp, holds atomComp* from const file.
        For atomTypeMath, holds atomMath* from const file.
        """

        self.arg1 = None
        """
        For all types besides atomTypeVal, contains reference to child atom.
        """

        self.arg2 = None
        """
        For all types besides atomTypeVal, contains reference to child atom.
        """

        self.carrier = None
        """
        For atomTypeValRef, contains reference to some location.
        """

        self.attribute = None
        """
        For atomTypeValRef, contains reference to attribute in some location.
        """

        self.value = None
        """
        For atomTypeVal, contains pre-stored atom value.
        """

    def validateTree(self):
        """Validate full condition tree, given we're checking top-level node"""
        # Top-level node can be either logical join or comparison
        allowedTypes = {const.atomTypeLogic, const.atomTypeComp}
        if not self.type in allowedTypes:
            return False
        return self.__validateNode()


    def __validateNode(self):
        """Validates object fields"""
        validationRouter = {const.atomTypeLogic: self.__valLogic,
                            const.atomTypeComp: self.__valComp,
                            const.atomTypeMath: self.__valMath,
                            const.atomTypeValRef: self.__valValRef,
                            const.atomTypeVal: self.__valVal}
        try:
            method = validationRouter[self.type]
        except KeyError:
            return False
        return method()

    def __valLogic(self):
        if self.carrier is not None or self.attribute is not None or \
        self.value is not None:
            return False
        allowedSubtypes = {const.atomTypeLogic, const.atomTypeComp}
        try:
            if not self.arg1.type in allowedSubtypes or not self.arg1.type in allowedSubtypes:
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
        allowedSubtypes = {const.atomTypeMath, const.atomTypeValRef, const.atomTypeVal}
        try:
            if not self.arg1.type in allowedSubtypes or not self.arg1.type in allowedSubtypes:
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
        allowedSubtypes = {const.atomTypeMath, const.atomTypeValRef, const.atomTypeVal}
        try:
            if not self.arg1.type in allowedSubtypes or not self.arg1.type in allowedSubtypes:
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
        if self.value:
            return False
        return True

    def printTree(self, indent=""):
        """Convert atom tree, starting from self, to string"""
        # Scatter logic operator and its arguments into several lines with different
        # indentation level
        if self.type == const.atomTypeLogic:
            logicLiterals = {const.atomLogicAnd: "and",
                             const.atomLogicOr: "or"}
            newindent = "  {0}".format(indent)
            result = "{2}\n{0}{1}\n{3}".format(indent, logicLiterals[self.operator], self.arg1.printTree(indent=newindent), self.arg2.printTree(indent=newindent))
        # Print comparison on the same line with its arguments, just place them in brackets
        elif self.type == const.atomTypeComp:
            compLiterals = {const.atomCompEq: "==",
                            const.atomCompNotEq: "!=",
                            const.atomCompLess: "<",
                            const.atomCompLessEq: "<=",
                            const.atomCompGreat: ">",
                            const.atomCompGreatEq: ">="}
            newindent = "  {0}".format(indent)
            result = "{0}({2}) {1} ({3})".format(indent, compLiterals[self.operator], self.arg1.printTree(), self.arg2.printTree())
        # Math operations are printed on the same line with its arguments
        elif self.type == const.atomTypeMath:
            mathLiterals = {const.atomMathAdd: "+",
                            const.atomMathSub: "-"}
            newindent = "  {0}".format(indent)
            result = "{0}{2} {1} {3}".format(indent, mathLiterals[self.operator], self.arg1.printTree(), self.arg2.printTree())
        # Tag carrier location with c, its attribute with a
        elif self.type == const.atomTypeValRef:
            result = "c{0}.a{1}".format(self.carrier, self.attribute)
        # Print hardcoded values with v tag
        elif self.type == const.atomTypeVal:
            result = "v{0}".format(self.value)
        return result
