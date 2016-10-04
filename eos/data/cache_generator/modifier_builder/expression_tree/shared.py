# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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
# ===============================================================================


"""
This file is intended to hold some functions and data, which
is used by several converters.
"""


from collections import namedtuple

from eos.const.eos import State, Scope
from eos.const.eve import EffectCategory, Operand


# Named tuple for ease of access of operand metadata, where:
# enabled -- defines if operand is enabled or disabled
# gang -- boolean, indicating if it is local or gang modifier
# mirror -- contains ID of operand which is "mirror"
OperandMeta = namedtuple('OperandMeta', ('enabled', 'gang', 'mirror'))


# Map which holds data auxiliary for converters
# Format: {operand: OperandMeta}
operand_data = {
    Operand.add_gang_grp_mod: OperandMeta(enabled=True, gang=True, mirror=Operand.rm_gang_grp_mod),
    Operand.add_gang_itm_mod: OperandMeta(enabled=True, gang=True, mirror=Operand.rm_gang_itm_mod),
    Operand.add_gang_own_srq_mod: OperandMeta(enabled=True, gang=True, mirror=Operand.rm_gang_own_srq_mod),
    Operand.add_gang_srq_mod: OperandMeta(enabled=True, gang=True, mirror=Operand.rm_gang_srq_mod),
    Operand.add_itm_mod: OperandMeta(enabled=True, gang=False, mirror=Operand.rm_itm_mod),
    Operand.add_loc_grp_mod: OperandMeta(enabled=True, gang=False, mirror=Operand.rm_loc_grp_mod),
    Operand.add_loc_mod: OperandMeta(enabled=True, gang=False, mirror=Operand.rm_loc_mod),
    Operand.add_loc_srq_mod: OperandMeta(enabled=True, gang=False, mirror=Operand.rm_loc_srq_mod),
    Operand.add_own_srq_mod: OperandMeta(enabled=True, gang=False, mirror=Operand.rm_own_srq_mod),
    Operand.rm_gang_grp_mod: OperandMeta(enabled=True, gang=True, mirror=Operand.add_gang_grp_mod),
    Operand.rm_gang_itm_mod: OperandMeta(enabled=True, gang=True, mirror=Operand.add_gang_itm_mod),
    Operand.rm_gang_own_srq_mod: OperandMeta(enabled=True, gang=True, mirror=Operand.add_gang_own_srq_mod),
    Operand.rm_gang_srq_mod: OperandMeta(enabled=True, gang=True, mirror=Operand.add_gang_srq_mod),
    Operand.rm_itm_mod: OperandMeta(enabled=True, gang=False, mirror=Operand.add_itm_mod),
    Operand.rm_loc_grp_mod: OperandMeta(enabled=True, gang=False, mirror=Operand.add_loc_grp_mod),
    Operand.rm_loc_mod: OperandMeta(enabled=True, gang=False, mirror=Operand.add_loc_mod),
    Operand.rm_loc_srq_mod: OperandMeta(enabled=True, gang=False, mirror=Operand.add_loc_srq_mod),
    Operand.rm_own_srq_mod: OperandMeta(enabled=True, gang=False, mirror=Operand.add_own_srq_mod),
    Operand.attack: OperandMeta(enabled=False, gang=None, mirror=None),
    Operand.cargo_scan: OperandMeta(enabled=False, gang=None, mirror=None),
    Operand.cheat_tele_dock: OperandMeta(enabled=False, gang=None, mirror=None),
    Operand.cheat_tele_gate: OperandMeta(enabled=False, gang=None, mirror=None),
    Operand.aoe_decloak: OperandMeta(enabled=False, gang=None, mirror=None),
    Operand.ecm_burst: OperandMeta(enabled=False, gang=None, mirror=None),
    Operand.aoe_dmg: OperandMeta(enabled=False, gang=None, mirror=None),
    Operand.missile_launch: OperandMeta(enabled=False, gang=None, mirror=None),
    Operand.defender_launch: OperandMeta(enabled=False, gang=None, mirror=None),
    Operand.fof_launch: OperandMeta(enabled=False, gang=None, mirror=None),
    Operand.mine: OperandMeta(enabled=False, gang=None, mirror=None),
    Operand.power_booster: OperandMeta(enabled=False, gang=None, mirror=None),
    Operand.ship_scan: OperandMeta(enabled=False, gang=None, mirror=None),
    Operand.survey_scan: OperandMeta(enabled=False, gang=None, mirror=None),
    Operand.tgt_hostile: OperandMeta(enabled=False, gang=None, mirror=None),
    Operand.tgt_silent: OperandMeta(enabled=False, gang=None, mirror=None),
    Operand.tool_tgt_skills: OperandMeta(enabled=False, gang=None, mirror=None),
    Operand.user_error: OperandMeta(enabled=False, gang=None, mirror=None),
    Operand.vrf_tgt_grp: OperandMeta(enabled=False, gang=None, mirror=None)
}

# Dictionary which assists conversion of effect category
# and operand gang/local modification to state and scope
# Format: {(effect category, gang flag): (state, scope)}
state_data = {
    (EffectCategory.passive, False): (State.offline, Scope.local),
    (EffectCategory.passive, True): (State.offline, Scope.gang),
    (EffectCategory.active, False): (State.active, Scope.local),
    (EffectCategory.active, True): (State.active, Scope.gang),
    (EffectCategory.target, False): (State.active, Scope.projected),
    (EffectCategory.online, False): (State.online, Scope.local),
    (EffectCategory.online, True): (State.online, Scope.gang),
    (EffectCategory.overload, False): (State.overload, Scope.local),
    (EffectCategory.overload, True): (State.overload, Scope.gang),
    (EffectCategory.system, False): (State.offline, Scope.local),
    (EffectCategory.system, True): (State.offline, Scope.gang)
}
