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


from collections import namedtuple

from eos.eve.const import Operand


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
