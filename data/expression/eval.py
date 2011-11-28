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
from .info import ExpressionInfo, ExpressionFilter

class EvalException(Exception):
    pass

class ExpressionEval(object):
    """
    Expression evaluator responsible for converting a tree of Expression objects (which isn't directly useful to us)
    into one or several ExpressionInfo objects which can then be ran as needed.
    """
    def __init__(self):
        self.__activeExpression = None
        self.infos = []
        self.fail = False  # Stop guard, true if parsing this expression failed at some point

    def _prepare(self, owner, fit):
        """
        Internal method that prepares an eval object for application.
        """
        for e in self.infos:
            fit._prepare(owner, e)

    def _apply(self, owner, fit):
        """
        Internal run method that applies all expressions stored in this eval object.
        This is typically called for you by the expression itself
        """
        for e in self.infos:
            fit._apply(owner, e)

    def _undo(self, owner, fit):
        for e in self.infos:
            fit._undo(owner, e)

    def build(self, base):
        """
        Prepare an ExpressionEval object for running.
        No validations are done here, what is passed should be valid.
        If its not, exceptions will most likely occur, or you'll get an incomplete ExpressionInfo object as a result
        If this is not called before run()/undo() they will not do anything
        """
        # Validation: detect stubs, if a stub is found, return an empty list
        infos = self.infos
        if base.operand == const.opndDefInt and int(base.value) == 1:
            return infos

        try:
            self.__build(base)
        except EvalException as e:
            del self.infos[:]
            print(e.args[0])

        return self.infos

    def __build(self, element):
        """
        Internal recursive building method.
        The public build() passes the base to this method, which will then proceed to build it, as well as all its children
        into (hopefully) fully functional ExpressionInfo objects.
        """
        # Sanity guard
        if element is None or self.fail:
            return

        # Get some stuff locally, we refer it often
        activeExpression = self.__activeExpression

        # Check if expression is composite
        if element.operand == const.opndCombine:
            # If we already have an active expression, store it first.
            # This should be when combined expression is found somewhere down a tree
            if activeExpression is not None:
                self.infos.append(self.__activeExpression)

            # Build first expression
            self.__activeExpression = ExpressionInfo()
            self.__build(element.arg1)
            self.infos.append(self.__activeExpression)

            # Build second
            self.__activeExpression = ExpressionInfo()
            self.__build(element.arg2)
            self.infos.append(self.__activeExpression)

            # Done
            return

        elif activeExpression is None:
            self.__activeExpression = activeExpression = ExpressionInfo()
            self.infos.append(activeExpression)

        res1 = self.__build(element.arg1)
        res2 = self.__build(element.arg2)

        if element.operand in (const.opndAIM, const.opndALGM):
            activeExpression.sourceAttributeId = res2

        elif element.operand == const.opndItmAttr:
            return (res1, # Entity
                    res2) # Attribute

        elif element.operand == const.opndDefOper:
            try:
                return const.operConvMap[element.value]
            except KeyError:
                print("Unknown operator is used in expression")
                return

        elif element.operand == const.opndDefLoc:
            try:
                return const.locConvMap[element.value]
            except KeyError:
                print("Unknown location is used in expression")
                return

        elif element.operand in (const.opndDefGrp, const.opndDefType):
            return element.value

        elif element.operand == const.opndDefAttr:
            return element.attributeId

        elif element.operand == const.opndTgtOper:
            activeExpression.operation = res1
            activeExpression.target, activeExpression.targetAttributeId = res2

        elif element.operand == const.opndLG: # JoinGroupFilter
            activeExpression.filters.append(ExpressionFilter(const.filterLG, res2))
            return res1 # Entity, handled by parent

        elif element.operand == const.opndLRS: #JoinSkillFilter
            activeExpression.filters.append(ExpressionFilter(const.filterLRS, res2))
            return res1 # Entity, handled by parent
        else:
            raise EvalException("Failed to evaluate {0}".format(element.id))
