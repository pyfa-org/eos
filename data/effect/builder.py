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
from .info import EffectInfo

# Mirror modifications, top-level operands
mirrorMods = {const.opndAddGangGrpMod: const.opndRmGangGrpMod,
              const.opndAddGangItmMod: const.opndRmGangItmMod,
              const.opndAddGangOwnSrqMod: const.opndRmGangOwnSrqMod,
              const.opndAddGangSrqMod: const.opndRmGangSrqMod,
              const.opndAddItmMod: const.opndRmItmMod,
              const.opndAddLocGrpMod: const.opndRmLocGrpMod,
              const.opndAddLocMod: const.opndRmLocMod,
              const.opndAddLocSrqMod: const.opndRmLocSrqMod,
              const.opndAddOwnSrqMod: const.opndRmOwnSrqMod}
# Plain modifications list
modifiers = set(mirrorMods.keys()).union(set(mirrorMods.values()))

class Modifier(object):
    """
    Internal builder object, stores meaningful elements of expression tree temporarily
    """
    def __init__(self):
        # Type of modification
        self.type = None
        # Source attribute ID
        self.sourceAttribute = None
        # Operation to be applied on target
        self.operation = None
        # Target attribute ID
        self.targetAttribute = None
        # Target location for modification
        self.targetLocation = None
        # Target group ID of items
        self.targetGroup = None
        # Skill requirement ID of target items
        self.targetSkillRq = None

    # Set of validation methods
    def validate(self):
        """Self-validation for modifier objects"""
        # These fields always should be filled
        if self.operation is None or self.targetAttribute is None or \
        self.sourceAttribute is None:
            return False
        # Other fields are optional, check them using modifier type
        validateMap = {const.opndAddItmMod: self.__valItm,
                       const.opndRmItmMod: self.__valItm,
                       const.opndAddLocGrpMod: self.__valLocGrp,
                       const.opndRmLocGrpMod: self.__valLocGrp,
                       const.opndAddLocMod: self.__valLoc,
                       const.opndRmLocMod: self.__valLoc,
                       const.opndAddLocSrqMod: self.__valLocSrq,
                       const.opndRmLocSrqMod: self.__valLocSrq,
                       const.opndAddOwnSrqMod: self.__valOwnSrq,
                       const.opndRmOwnSrqMod: self.__valOwnSrq}
        try:
            method = validateMap[self.type]
        except KeyError:
            return False
        return method()

    def __valItm(self):
        if self.targetGroup is not None or self.targetSkillRq is not None:
            return False
        if self.targetLocation is None:
            return False
        return True

    def __valLocGrp(self):
        if self.targetSkillRq is not None:
            return False
        validLocs = (const.locChar, const.locShip, const.locTgt)
        if not self.targetLocation in validLocs or self.targetGroup is None:
            return False
        return True

    def __valLoc(self):
        if self.targetGroup is not None or self.targetSkillRq is not None:
            return False
        if self.targetLocation is None:
            return False
        return True

    def __valLocSrq(self):
        if self.targetGroup is not None:
            return False
        validLocs = (const.locChar, const.locShip, const.locTgt)
        if not self.targetLocation in validLocs or self.targetSkillRq is None:
            return False
        return True

    def __valOwnSrq(self):
        if self.targetGroup is not None:
            return False
        if self.targetLocation != const.locChar or self.targetSkillRq is None:
            return False
        return True

    def isMirror(self, other):
        """For duration modification, return True if one modifier complements another"""
        # First, check type, it should be mirror according to map
        if self.type in mirrorMods:
            if other.type != mirrorMods[self.type]:
                return False
        else:
            if self.type != mirrorMods[other.type]:
                return False
        # Then, check all other fields of modifier
        if self.sourceAttribute != other.sourceAttribute or self.operation != other.operation or \
        self.targetAttribute != other.targetAttribute or self.targetLocation != other.targetLocation or \
        self.targetGroup != other.targetGroup or self.targetSkillRq != other.targetSkillRq:
            return False
        # If all conditions were met, then it's actually mirror
        return True

    # Set of conversion functions
    def convertToInfo(self):
        """Convert Modifier object to EffectInfo object"""
        # Create object and fill generic fields
        info = EffectInfo()
        info.operation = self.operation
        info.sourceAttributeId = self.sourceAttribute
        info.targetAttributeId = self.targetAttribute
        # Fill remaining fields on per-modifier basis
        conversionMap = {const.opndAddItmMod: self.__convItm,
                         const.opndRmItmMod: self.__convItm,
                         const.opndAddLocGrpMod: self.__convLocGrp,
                         const.opndRmLocGrpMod: self.__convLocGrp,
                         const.opndAddLocMod: self.__convLoc,
                         const.opndRmLocMod: self.__convLoc,
                         const.opndAddLocSrqMod: self.__convLocSrq,
                         const.opndRmLocSrqMod: self.__convLocSrq,
                         const.opndAddOwnSrqMod: self.__convOwnSrq,
                         const.opndRmOwnSrqMod: self.__convOwnSrq}
        conversionMap[self.type](info)
        return info

    def __convItm(self, info):
        info.location = self.targetLocation

    def __convLocGrp(self, info):
        info.location = self.targetLocation
        info.filterType = const.filterGroup
        info.filterValue = self.targetGroup

    def __convLoc(self, info):
        info.location = self.targetLocation
        info.filterType = const.filterAll

    def __convLocSrq(self, info):
        info.location = self.targetLocation
        info.filterType = const.filterSkill
        info.filterValue = self.targetSkillRq

    def __convOwnSrq(self, info):
        info.location = const.locSpace
        info.filterType = const.filterSkill
        info.filterValue = self.targetSkillRq


class InfoBuilder(object):
    """
    EffectInfo is responsible for converting two trees (pre and post) of Expression objects (which
    aren't directly useful to us) into EffectInfo objects which can then be used as needed.
    """
    def __init__(self):
        # List for EffectInfos which we will return
        self.infos = []
        # Modifiers we got out of preExpression
        self.preMods = []
        # Modifiers we got out of postExpression
        self.postMods = []
        # Which modifier list we're using at the moment
        self.activeList = None
        # Which modifier we're referencing at the moment
        self.activeMod = None

    def build(self, preExpression, postExpression):
        """
        Go through both trees and compose our EffectInfos
        """
        self.activeList = self.preMods
        try:
            print("Building pre-expression tree with base {}".format(preExpression.id))
            self.__generic(preExpression)
        except:
            self.preMods = []
            print("Error building pre-expression tree with base {}".format(preExpression.id))
        for mod in self.preMods:
            if mod.validate() is not True:
                print("Invalid pre")
                return []

        self.activeList = self.postMods
        try:
            print("Building post-expression tree with base {}".format(postExpression.id))
            self.__generic(postExpression)
        except:
            self.postMods = []
            print("Error building post-expression tree with base {}".format(postExpression.id))
        for mod in self.postMods:
            if mod.validate() is not True:
                print("Invalid post")
                return []

        for preMod in self.preMods:
            for postMod in self.postMods:
                if preMod.isMirror(postMod) is True:
                    info = preMod.convertToInfo()
                    self.infos.append(info)
                    break

        return self.infos

    # Top-level methods - combining, routing, etc
    def __generic(self, element):
        """Generic entry point, used if we expect passed element to be meaningful"""
        if element.operand in modifiers:
            self.__makeModifier(element)
        else:
            genericOpnds = {const.opndSplice: self.__splice}
            genericOpnds[element.operand](element)

    def __splice(self, element):
        """Reference two expressions from self"""
        self.__generic(element.arg1)
        self.__generic(element.arg2)

    def __makeModifier(self, element):
        """Make info according to passed data"""
        # Make modifier object and let builder know we're working with it
        self.activeMod = Modifier()
        # Write modifier type, which corresponds to top-level operand of modification
        self.activeMod.type = element.operand
        # Request operator and target data, it's always in arg1
        self.__optrTgt(element.arg1)
        # Write down source attribute from arg2
        self.activeMod.sourceAttribute = self.__getAttr(element.arg2)
        # Append filled modifier to list we're currently working with
        self.activeList.append(self.activeMod)
        # If something weird happens, clean current modifier to throw
        # exceptions instead of filling old modifier if something goes wrong
        self.activeMod = None

    def __optrTgt(self, element):
        """Join operator and target definition"""
        # Operation is always in arg1
        self.activeMod.operation = self.__getOptr(element.arg1)
        # Handling of arg2 depends on its operand
        tgtRouteMap = {const.opndGenAttr: self.__tgtAttr,
                       const.opndGrpAttr: self.__tgtGrpAttr,
                       const.opndSrqAttr: self.__tgtSrqAttr,
                       const.opndItmAttr: self.__tgtItmAttr}
        tgtRouteMap[element.arg2.operand](element.arg2)

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
        itmGetterMap = {const.opndDefLoc: self.__tgtItm,
                        const.opndLocGrp: self.__tgtLocGrp,
                        const.opndLocSrq: self.__tgtLocSrq}
        itmGetterMap[element.arg1.operand](element.arg1)
        # Target attribute is always specified in arg2
        self.activeMod.targetAttribute = self.__getAttr(element.arg2)

    def __tgtItm(self, element):
        """Get target location and store it"""
        self.activeMod.target = self.__getLoc(element)

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
        return element.typeId
