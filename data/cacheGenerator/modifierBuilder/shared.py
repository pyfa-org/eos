#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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

from eos.const import State, Context
from eos.eve.const import EffectCategory, Operand


# Named tuple for ease of access of operand metadata, where:
# type -- OperandType class' attribute value
# gang -- boolean, indicating if it is local or gang modifier
# mirror -- contains ID of operand which is "mirror"
OperandMeta = namedtuple('OperandMeta', ('enabled', 'gang', 'mirror'))


# Map which holds data auxiliary for builder
# Format: {operand: OperandMeta}
operandData = {Operand.addGangGrpMod: OperandMeta(enabled=True, gang=True, mirror=Operand.rmGangGrpMod),
               Operand.addGangItmMod: OperandMeta(enabled=True, gang=True, mirror=Operand.rmGangItmMod),
               Operand.addGangOwnSrqMod: OperandMeta(enabled=True, gang=True, mirror=Operand.rmGangOwnSrqMod),
               Operand.addGangSrqMod: OperandMeta(enabled=True, gang=True, mirror=Operand.rmGangSrqMod),
               Operand.addItmMod: OperandMeta(enabled=True, gang=False, mirror=Operand.rmItmMod),
               Operand.addLocGrpMod: OperandMeta(enabled=True, gang=False, mirror=Operand.rmLocGrpMod),
               Operand.addLocMod: OperandMeta(enabled=True, gang=False, mirror=Operand.rmLocMod),
               Operand.addLocSrqMod: OperandMeta(enabled=True, gang=False, mirror=Operand.rmLocSrqMod),
               Operand.addOwnSrqMod: OperandMeta(enabled=True, gang=False, mirror=Operand.rmOwnSrqMod),
               Operand.rmGangGrpMod: OperandMeta(enabled=True, gang=True, mirror=Operand.addGangGrpMod),
               Operand.rmGangItmMod: OperandMeta(enabled=True, gang=True, mirror=Operand.addGangItmMod),
               Operand.rmGangOwnSrqMod: OperandMeta(enabled=True, gang=True, mirror=Operand.addGangOwnSrqMod),
               Operand.rmGangSrqMod: OperandMeta(enabled=True, gang=True, mirror=Operand.addGangSrqMod),
               Operand.rmItmMod: OperandMeta(enabled=True, gang=False, mirror=Operand.addItmMod),
               Operand.rmLocGrpMod: OperandMeta(enabled=True, gang=False, mirror=Operand.addLocGrpMod),
               Operand.rmLocMod: OperandMeta(enabled=True, gang=False, mirror=Operand.addLocMod),
               Operand.rmLocSrqMod: OperandMeta(enabled=True, gang=False, mirror=Operand.addLocSrqMod),
               Operand.rmOwnSrqMod: OperandMeta(enabled=True, gang=False, mirror=Operand.addOwnSrqMod),
               Operand.attack: OperandMeta(enabled=False, gang=None, mirror=None),
               Operand.cargoScan: OperandMeta(enabled=False, gang=None, mirror=None),
               Operand.cheatTeleDock: OperandMeta(enabled=False, gang=None, mirror=None),
               Operand.cheatTeleGate: OperandMeta(enabled=False, gang=None, mirror=None),
               Operand.aoeDecloak: OperandMeta(enabled=False, gang=None, mirror=None),
               Operand.ecmBurst: OperandMeta(enabled=False, gang=None, mirror=None),
               Operand.aoeDmg: OperandMeta(enabled=False, gang=None, mirror=None),
               Operand.missileLaunch: OperandMeta(enabled=False, gang=None, mirror=None),
               Operand.defenderLaunch: OperandMeta(enabled=False, gang=None, mirror=None),
               Operand.fofLaunch: OperandMeta(enabled=False, gang=None, mirror=None),
               Operand.mine: OperandMeta(enabled=False, gang=None, mirror=None),
               Operand.powerBooster: OperandMeta(enabled=False, gang=None, mirror=None),
               Operand.shipScan: OperandMeta(enabled=False, gang=None, mirror=None),
               Operand.surveyScan: OperandMeta(enabled=False, gang=None, mirror=None),
               Operand.tgtHostile: OperandMeta(enabled=False, gang=None, mirror=None),
               Operand.tgtSilent: OperandMeta(enabled=False, gang=None, mirror=None),
               Operand.toolTgtSkills: OperandMeta(enabled=False, gang=None, mirror=None),
               Operand.userError: OperandMeta(enabled=False, gang=None, mirror=None),
               Operand.vrfTgtGrp: OperandMeta(enabled=False, gang=None, mirror=None)}

# Dictionary which assists conversion of effect category
# and operand gang/local modification to state and context
# Format: {(effect category, gang flag): (state, context)}
stateData = {(EffectCategory.passive, False): (State.offline, Context.local),
             (EffectCategory.passive, True): (State.offline, Context.gang),
             (EffectCategory.active, False): (State.active, Context.local),
             (EffectCategory.active, True): (State.active, Context.gang),
             (EffectCategory.target, False): (State.active, Context.projected),
             (EffectCategory.online, False): (State.online, Context.local),
             (EffectCategory.online, True): (State.online, Context.gang),
             (EffectCategory.overload, False): (State.overload, Context.local),
             (EffectCategory.overload, True): (State.overload, Context.gang),
             (EffectCategory.system, False): (State.offline, Context.local),
             (EffectCategory.system, True): (State.offline, Context.gang)}
