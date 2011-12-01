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
        except:
            del self.infos[:]
            print("Error building expression tree with base {}".format(base.id))

        for info in self.infos:
            if info.validate() is not True:
                del self.infos[:]
                print("Error validating one of the infos of expression tree with base {}".format(base.id))
                break

        return self.infos

    # Top-level methods - combining, routing, etc
    def __generic(self, element):
        """Generic entry point, used if we expect passed element to be meaningful"""
        genericOpnds = {const.opndSplice: self.__splice,
                        const.opndAddGangGrpMod: self.__addGangGrpMod,
                        const.opndAddGangItmMod: self.__addGangItmMod,
                        const.opndAddGangSrqMod: self.__addGangSrqMod,
                        const.opndAddItmMod: self.__addItmMod,
                        const.opndAddLocGrpMod: self.__addLocGrpMod,
                        const.opndAddLocMod: self.__addLocMod,
                        const.opndAddLocSrqMod: self.__addLocSrqMod,
                        const.opndAddOwnSrqMod: self.__addOwnSrqMod}
        genericOpnds[element.operand](element)

    def __splice(self, element):
        """Reference two expressions from self"""
        self.__generic(element.arg1)
        self.__generic(element.arg2)

    # Fit-local modifications
    def __addItmMod(self, element):
        """Add modification directly to item"""
        info = ExpressionInfo()
        info.type = const.infoAddItmMod
        self.__optrTgt(element.arg1, info)
        info.sourceAttributeId = self.__getAttr(element.arg2)
        self.infos.append(info)

    def __addLocGrpMod(self, element):
        """Add modification to items with location and group filters"""
        info = ExpressionInfo()
        info.type = const.infoAddLocGrpMod
        self.__optrTgt(element.arg1, info)
        info.sourceAttributeId = self.__getAttr(element.arg2)
        self.infos.append(info)

    def __addLocMod(self, element):
        """Add modification to items with location filter"""
        info = ExpressionInfo()
        info.type = const.infoAddLocMod
        self.__optrTgt(element.arg1, info)
        info.sourceAttributeId = self.__getAttr(element.arg2)
        self.infos.append(info)

    def __addLocSrqMod(self, element):
        """Add modification to items with location and skill requirement filters"""
        info = ExpressionInfo()
        info.type = const.infoAddLocSrqMod
        self.__optrTgt(element.arg1, info)
        info.sourceAttributeId = self.__getAttr(element.arg2)
        self.infos.append(info)

    def __addOwnSrqMod(self, element):
        """Add modification to items with owner and skill requirement filters"""
        info = ExpressionInfo()
        info.type = const.infoAddOwnSrqMod
        self.__optrTgt(element.arg1, info)
        info.sourceAttributeId = self.__getAttr(element.arg2)
        self.infos.append(info)

    # Gang modifications
    def __addGangGrpMod(self, element):
        """Add modification to gang-mates' items with group filter"""
        info = ExpressionInfo()
        info.type = const.infoAddGangGrpMod
        self.__optrTgt(element.arg1, info)
        info.sourceAttributeId = self.__getAttr(element.arg2)
        self.infos.append(info)

    def __addGangItmMod(self, element):
        """Add modification directly to gang-mates"""
        info = ExpressionInfo()
        info.type = const.infoAddGangItmMod
        self.__optrTgt(element.arg1, info)
        info.sourceAttributeId = self.__getAttr(element.arg2)
        self.infos.append(info)

    def __addGangOwnSrqMod(self, element):
        """Add modification to gang-mates' items with owner and skill requirement filters"""
        info = ExpressionInfo()
        info.type = const.infoAddGangOwnSrqMod
        self.__optrTgt(element.arg1, info)
        info.sourceAttributeId = self.__getAttr(element.arg2)
        self.infos.append(info)

    def __addGangSrqMod(self, element):
        """Add modification to gang-mates' items with skill requirement filter"""
        info = ExpressionInfo()
        info.type = const.infoAddGangSrqMod
        self.__optrTgt(element.arg1, info)
        info.sourceAttributeId = self.__getAttr(element.arg2)
        self.infos.append(info)

    # Bottom-level servicing methods
    def __optrTgt(self, element, info):
        """Join operator and target definition"""
        info.operation = self.__getOptr(element.arg1)
        tgtRouteMap = {const.opndItmAttr: self.__itmAttr,
                       const.opndGenAttr: self.__attr,
                       const.opndSrqAttr: self.__srqAttr,
                       const.opndGrpAttr: self.__grpAttr}
        tgtRouteMap[element.arg2.operand](element.arg2, info)

    def __itmAttr(self, element, info):
        """Join target item specification and target attribute"""
        itmGetterMap = {const.opndDefLoc: self.__loc,
                        const.opndLocGrp: self.__locGrp,
                        const.opndLocSrq: self.__locSrq}
        itmGetterMap[element.arg1.operand](element.arg1, info)
        info.targetAttributeId = self.__getAttr(element.arg2)

    def __attr(self, element, info):
        """Get attribute and stores it"""
        info.targetAttributeId = self.__getAttr(element.arg1)

    def __loc(self, element, info):
        """Get location and store it"""
        info.target = self.__getLoc(element)

    def __grpAttr(self, element, info):
        """Join target group and target attribute"""
        info.target = self.__getGrp(element.arg1)
        info.targetAttributeId = self.__getAttr(element.arg2)

    def __srqAttr(self, element, info):
        """Join target skill requirement and target attribute"""
        info.target = self.__getType(element.arg1)
        info.targetAttributeId = self.__getAttr(element.arg2)

    def __locGrp(self, element, info):
        """Join target location filter and group filter"""
        info.target = (self.__getLoc(element.arg1), self.__getGrp(element.arg2))

    def __locSrq(self, element, info):
        """Join target location filter and skill requirement filter"""
        info.target = (self.__getLoc(element.arg1), self.__getType(element.arg2))

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
        return element.typeId
