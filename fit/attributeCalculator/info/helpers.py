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


"""
This file is intended to hold some functions and data, which
is used by several builders.
"""


from collections import namedtuple

from eos.const import Location, Operator, InvType
from eos.eve.const import Operand


class ExpressionData:
    """
    Provides access to expression data with conversion
    jobs where necessary.
    """

    @classmethod
    def getOperator(cls, expression):
        """Helper for modifying expressions, defines operator"""
        # Format: {operator name: operator ID}
        conversionMap = {"PreAssignment": Operator.preAssignment,
                         "PreMul": Operator.preMul,
                         "PreDiv": Operator.preDiv,
                         "ModAdd": Operator.modAdd,
                         "ModSub": Operator.modSub,
                         "PostMul": Operator.postMul,
                         "PostDiv": Operator.postDiv,
                         "PostPercent": Operator.postPercent,
                         "PostAssignment": Operator.postAssignment}
        operator = conversionMap[expression.value]
        return operator

    @classmethod
    def getLocation(cls, expression):
        """Define location"""
        # Format: {location name: location ID}
        conversionMap = {"Self": Location.self_,
                         "Char": Location.character,
                         "Ship": Location.ship,
                         "Target": Location.target,
                         "Other": Location.other,
                         "Area": Location.area}
        location = conversionMap[expression.value]
        return location

    @classmethod
    def getAttribute(cls, expression):
        """Reference attribute via ID"""
        attribute = int(expression.expressionAttributeId)
        return attribute

    @classmethod
    def getGroup(cls, expression):
        """Reference group via ID"""
        group = int(expression.expressionGroupId)
        return group

    @classmethod
    def getType(cls, expression):
        """Reference type via ID"""
        # Type getter function has special handling
        if expression.operandId == Operand.getType:
            # Currently, we have only ID representing self type getter, so run
            # additional check if type getter is for self
            if cls.getLocation(expression.arg1) == Location.self_:
                return InvType.self_
            else:
                return None
        else:
            type_ = int(expression.expressionTypeId)
            return type_

    @classmethod
    def getInteger(cls, expression):
        """Get integer from value"""
        integer = int(expression.value)
        return integer

    @classmethod
    def getBoolean(cls, expression):
        """Get integer from value"""
        # Format: {boolean name: boolean value}
        conversionMap = {"True": True,
                         "False": False}
        boolean = conversionMap[expression.value]
        return boolean


# Named tuple for ease of access of operand metadata, where:
# type -- OperandType class' attribute value
# gang -- boolean, indicating if it is local or gang modifier
# mirror -- contains ID of operand which is "mirror"
OperandMeta = namedtuple("OperandMeta", ("type", "gang", "mirror"))


class OperandType:
    """Modifier operand type ID holder"""
    duration = 1
    instant = 2
    inactive = 3


# Map which holds data auxiliary for builder
# Format: {operand: OperandMeta}
operandData = {Operand.addGangGrpMod: OperandMeta(type=OperandType.duration, gang=True, mirror=Operand.rmGangGrpMod),
               Operand.addGangItmMod: OperandMeta(type=OperandType.duration, gang=True, mirror=Operand.rmGangItmMod),
               Operand.addGangOwnSrqMod: OperandMeta(type=OperandType.duration, gang=True, mirror=Operand.rmGangOwnSrqMod),
               Operand.addGangSrqMod: OperandMeta(type=OperandType.duration, gang=True, mirror=Operand.rmGangSrqMod),
               Operand.addItmMod: OperandMeta(type=OperandType.duration, gang=False, mirror=Operand.rmItmMod),
               Operand.addLocGrpMod: OperandMeta(type=OperandType.duration, gang=False, mirror=Operand.rmLocGrpMod),
               Operand.addLocMod: OperandMeta(type=OperandType.duration, gang=False, mirror=Operand.rmLocMod),
               Operand.addLocSrqMod: OperandMeta(type=OperandType.duration, gang=False, mirror=Operand.rmLocSrqMod),
               Operand.addOwnSrqMod: OperandMeta(type=OperandType.duration, gang=False, mirror=Operand.rmOwnSrqMod),
               Operand.rmGangGrpMod: OperandMeta(type=OperandType.duration, gang=True, mirror=Operand.addGangGrpMod),
               Operand.rmGangItmMod: OperandMeta(type=OperandType.duration, gang=True, mirror=Operand.addGangItmMod),
               Operand.rmGangOwnSrqMod: OperandMeta(type=OperandType.duration, gang=True, mirror=Operand.addGangOwnSrqMod),
               Operand.rmGangSrqMod: OperandMeta(type=OperandType.duration, gang=True, mirror=Operand.addGangSrqMod),
               Operand.rmItmMod: OperandMeta(type=OperandType.duration, gang=False, mirror=Operand.addItmMod),
               Operand.rmLocGrpMod: OperandMeta(type=OperandType.duration, gang=False, mirror=Operand.addLocGrpMod),
               Operand.rmLocMod: OperandMeta(type=OperandType.duration, gang=False, mirror=Operand.addLocMod),
               Operand.rmLocSrqMod: OperandMeta(type=OperandType.duration, gang=False, mirror=Operand.addLocSrqMod),
               Operand.rmOwnSrqMod: OperandMeta(type=OperandType.duration, gang=False, mirror=Operand.addOwnSrqMod),
               Operand.assign: OperandMeta(type=OperandType.instant, gang=False, mirror=None),
               Operand.inc: OperandMeta(type=OperandType.instant, gang=False, mirror=None),
               Operand.dec: OperandMeta(type=OperandType.instant, gang=False, mirror=None),
               Operand.attack: OperandMeta(type=OperandType.inactive, gang=None, mirror=None),
               Operand.cargoScan: OperandMeta(type=OperandType.inactive, gang=None, mirror=None),
               Operand.cheatTeleDock: OperandMeta(type=OperandType.inactive, gang=None, mirror=None),
               Operand.cheatTeleGate: OperandMeta(type=OperandType.inactive, gang=None, mirror=None),
               Operand.aoeDecloak: OperandMeta(type=OperandType.inactive, gang=None, mirror=None),
               Operand.ecmBurst: OperandMeta(type=OperandType.inactive, gang=None, mirror=None),
               Operand.aoeDmg: OperandMeta(type=OperandType.inactive, gang=None, mirror=None),
               Operand.missileLaunch: OperandMeta(type=OperandType.inactive, gang=None, mirror=None),
               Operand.defenderLaunch: OperandMeta(type=OperandType.inactive, gang=None, mirror=None),
               Operand.fofLaunch: OperandMeta(type=OperandType.inactive, gang=None, mirror=None),
               Operand.mine: OperandMeta(type=OperandType.inactive, gang=None, mirror=None),
               Operand.powerBooster: OperandMeta(type=OperandType.inactive, gang=None, mirror=None),
               Operand.shipScan: OperandMeta(type=OperandType.inactive, gang=None, mirror=None),
               Operand.surveyScan: OperandMeta(type=OperandType.inactive, gang=None, mirror=None),
               Operand.tgtHostile: OperandMeta(type=OperandType.inactive, gang=None, mirror=None),
               Operand.tgtSilent: OperandMeta(type=OperandType.inactive, gang=None, mirror=None),
               Operand.toolTgtSkills: OperandMeta(type=OperandType.inactive, gang=None, mirror=None),
               Operand.userError: OperandMeta(type=OperandType.inactive, gang=None, mirror=None),
               Operand.vrfTgtGrp: OperandMeta(type=OperandType.inactive, gang=None, mirror=None)}
