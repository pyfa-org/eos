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
from .info import ExpressionInfo

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
            print("Building expression tree with base {}".format(base.id))
            self.__generic(base)
        except EvalException as e:
            del self.infos[:]
            print("Error parsing tree {}: {}".format(base.id, e.args[0]))

        return self.infos

    ### Alternative parser implementation ###

    def __generic(self, element):
        """Generic entry point, used if we expect passed element to be meaningful"""
        genericOpnds = {const.opndSplice: self.__splice,
                        const.opndAddItmMod: self.__addItmMod}
        try:
            genericMethod = genericOpnds[element.operand]
        except KeyError:
            raise EvalException("unknown operand in generic expression {}".format(element.id))
        genericMethod(element)

    def __splice(self, element):
        """Auxiliary combining expression, lets to reference multiple meaningful expressions from one"""
        # Pre-checks
        if element.arg1 is None or element.arg2 is None:
            raise EvalException("child is missing in splice expression {}".format(element.id))
        # Data processing
        self.__generic(element.arg1)
        self.__generic(element.arg2)

    def __addItmMod(self, element):
        """Modifying expression, adds modification directly to item"""
        # Pre-checks
        if element.arg1 is None or element.arg2 is None:
            raise EvalException("child is missing in addItmMod expression {}".format(element.id))
        # Data processing
        info = ExpressionInfo()
        info.type = const.infoAddItmMod
        self.__tgtOptr(element.arg1, info)
        info.sourceAttributeId = self.__getAttrId(element.arg2)
        # Post-checks
        if info.filter is not None:
            raise EvalException("filter has been set in addItmMod expression {}".format(element.id))
        if info.target is None:
            raise EvalException("no target in addItmMod expression {}".format(element.id))
        if info.targetAttributeId is None:
            raise EvalException("no target attribute in addItmMod expression {}".format(element.id))
        if info.sourceAttributeId is None:
            raise EvalException("no source attribute in addItmMod expression {}".format(element.id))
        self.infos.append(info)

    def __tgtOptr(self, element, info):
        """Helper for modifying expressions, joins target attribute of items and info operator"""
        # pre-checks
        if element.operand != const.opndTgtOptr:
            raise EvalException("operand mismatch in tgtOptr expression {}".format(element.id))
        if element.arg1 is None or element.arg2 is None:
            raise EvalException("child is missing in tgtOptr expression {}".format(element.id))
        # Data processing
        info.operation = self.__getOptr(element.arg1)
        self.__itmAttr(element.arg2, info)

    def __itmAttr(self, element, info):
        """Helper for modifying expressions, joins target items with target attribute"""
        # Pre-checks
        if element.operand != const.opndItmAttr:
            raise EvalException("operand mismatch in itmAttr expression {}".format(element.id))
        if element.arg1 is None or element.arg2 is None:
            raise EvalException("child is missing in itmAttr expression {}".format(element.id))
        # Data processing
        info.target = self.__getLoc(element.arg1)
        info.targetAttributeId = self.__getAttrId(element.arg2)

    def __getAttrId(self, element):
        """Helper for modifying expressions, references attribute via ID"""
        # Pre-checks
        if element.operand != const.opndDefAttr:
            raise EvalException("operand mismatch in defAttr expression {}".format(element.id))
        if not element.attributeId:
            raise EvalException("attribute ID specifier is empty in defAttr expression {}".format(element.id))
        # Data processing
        return element.attributeId

    def __getOptr(self, element):
        """Helper for modifying expressions, defines operator"""
        # Pre-checks
        if element.operand != const.opndDefOptr:
            raise EvalException("operand mismatch in defOptr expression {}".format(element.id))
        if not element.value:
            raise EvalException("value specifier is empty in defOptr expression {}".format(element.id))
        # Data processing and integrity check
        try:
            return const.optrConvMap[element.value]
        except KeyError:
            raise EvalException("unknown operator in defOptr expression {}".format(element.id))

    def __getLoc(self, element):
        """Helper for modifying expressions, defines location"""
        # Pre-checks
        if element.operand != const.opndDefLoc:
            raise EvalException("operand mismatch in defLoc expression {}".format(element.id))
        if not element.value:
            raise EvalException("value specifier is empty in defLoc expression {}".format(element.id))
        # Data processing and integrity check
        try:
            loc = const.locConvMap[element.value]
        except KeyError:
            raise EvalException("unknown location in defLoc expression {}".format(element.id))
        return loc
