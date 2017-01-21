# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2017 Anton Vorobyov
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
This file holds IDs of multiple Eos-specific entities.
"""

from enum import IntEnum, unique


@unique
class State(IntEnum):
    """
    Possible item states, used as part of public API and
    internally by Modifier class and classes interacting with
    it
    """
    # Values assigned to states are not deliberate, they must
    # be in ascending order. It means that e.g. online module
    # state, which should trigger modules' online and offline
    # effects/modifiers, must have higher value than offline,
    # and so on.
    offline = 1
    online = 2
    active = 3
    overload = 4


@unique
class Slot(IntEnum):
    module_high = 1
    module_med = 2
    module_low = 3
    rig = 4
    subsystem = 5
    turret = 6
    launcher = 7


@unique
class EffectBuildStatus(IntEnum):
    not_built = 1
    skipped = 2
    error = 3
    success_partial = 4
    success_full = 5


@unique
class ModifierType(IntEnum):
    item = 1
    location = 2
    location_group = 3
    location_skillrq = 4
    owner_skillrq = 5


@unique
class ModifierDomain(IntEnum):
    self = 1  # Self, i.e. carrier of modification source
    character = 2
    ship = 3
    target = 4
    other = 5  # Module for charge, charge for module


@unique
class ModifierOperator(IntEnum):
    pre_assign = 1
    pre_mul = 2
    pre_div = 3
    mod_add = 4
    mod_sub = 5
    post_mul = 6
    post_div = 7
    post_percent = 8
    post_assign = 9


@unique
class Restriction(IntEnum):
    cpu = 1
    powergrid = 2
    calibration = 3
    dronebay_volume = 4
    drone_bandwidth = 5
    launched_drone = 6
    drone_group = 7
    high_slot = 8
    medium_slot = 9
    low_slot = 10
    rig_slot = 11
    rig_size = 12
    subsystem_slot = 13
    subsystem_index = 14
    turret_slot = 15
    launcher_slot = 16
    implant_index = 17
    booster_index = 18
    ship_type_group = 19
    capital_item = 20
    max_group_fitted = 21
    max_group_online = 22
    max_group_active = 23
    skill_requirement = 24
    holder_class = 26
    state = 27
    charge_group = 28
    charge_size = 29
    charge_volume = 30
    booster_effect = 31

@unique
class EosEveTypes(IntEnum):
    """
    Container for Eos-specific type IDs. Any values defined
    here must not overlap with regular EVE type IDs.
    """
    current_self = -1
