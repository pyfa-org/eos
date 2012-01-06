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

from eos import const

class ConditionEval:
    """
    This class is used to evaluate the conditions on an info object and see if they are met
    """
    def __init__(self, info):
        self.info = info
        """The info object to evaluate for"""


    def isValid(self, holder):
        """
        public isvalid method. Checks if the condition is valid
        takes 1 argument: the holder against which to evaluate the condition
        """
        if self.info.conditions is None:
            return True
        else:
            return self.__isValid(holder, self.info.conditions)

    def __isValid(self, holder, atom):
        if atom.type == const.atomTypeLogic:
            arg1 = self.__isValid(holder, atom.arg1)
            arg2 = self.__isValid(holder, atom.arg2)

            if atom.operator == const.atomLogicAnd:
                return arg1 and arg2
            elif atom.operator == const.atomLogicOr:
                return arg1 or arg2

        elif atom.type == const.atomTypeComp:
            arg1 = self.__value(holder, atom.arg1)
            arg2 = self.__value(holder, atom.arg2)

            if atom.operator == const.atomCompEq:
                return arg1 == arg2
            elif atom.operator == const.atomCompNotEq:
                return arg1 != arg2
            elif atom.operator == const.atomCompLess:
                return arg1 < arg2
            elif atom.operator == const.atomCompLessEq:
                return arg1 <= arg2
            elif atom.operator == const.atomCompGreat:
                return arg1 > arg2
            elif atom.operator == const.atomCompGreatEq:
                return arg1 > arg2

    def __value(self, holder, atom):
        if atom.type == const.atomTypeMath:
            arg1 = self.__value(holder, atom.arg1)
            arg2 = self.__value(holder, atom.arg2)
            if atom.operator == const.atomMathAdd:
                return arg1 + arg2
            elif atom.operator == const.atomMathSub:
                return arg1 - arg2

        elif atom.type == const.atomTypeValRef:
            if atom.carrier == const.locSelf:
                target = holder
            elif atom.carrier == const.locChar:
                target = holder.fit.character
            elif atom.carrier == const.locShip:
                target = holder.fit.ship

            return target.attributes[atom.attribute]
        elif atom.type == const.atomTypeVal:
            return atom.value
