# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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
# ==============================================================================


"""
This file holds IDs of multiple Eos-specific entities.
"""


from enum import IntEnum
from enum import unique


@unique
class State(IntEnum):
    """Contains possible item states.

    Also used as effects' attribute to determine when this effect should be run.
    """
    # Values assigned to states are not deliberate, they must be in ascending
    # order. It means that e.g. online module state, which should trigger
    # modules' online and offline effects/modifiers, must have higher value
    # than offline, and so on.
    offline = 1
    online = 2
    active = 3
    overload = 4


@unique
class EffectMode(IntEnum):
    """Contains possible effect run modes.

    Run modes define under which conditions effects are run.
    """
    # In this mode rules vary, depending on effect category:
    # - Offline: effects from this category are run when item is in offline+
    # state, and when they do not have fitting usage chance specified
    # - Online: effects from this category are run when item is in online+
    # state, and when item has runnable 'online' effect
    # - Active: effects from this category are run when item is in active+
    # state, and only when effect is default item effect
    # - Overload: effects from this category are run when item is in overload+
    # state
    full_compliance = 1
    # Effects in this mode are always run if item's state is high enough to run
    # it
    state_compliance = 2
    # Effects in this mode are always running no matter what
    force_run = 3
    # Effects in this mode are never running no matter what
    force_stop = 4


@unique
class EffectBuildStatus(IntEnum):
    """Contains possible effect build statuses.

    Used for informational purposes only.
    """
    skipped = 1
    error = 2
    success_partial = 3
    success = 4
    custom = 5


@unique
class ModAffecteeFilter(IntEnum):
    """Contains possible modifier target filter types.

    Used during attribute calculation.
    """
    item = 1
    domain = 2  # Domain children only, excluding parent item
    domain_group = 3  # Domain children only, excluding parent item
    domain_skillrq = 4  # Domain children only, excluding parent item
    owner_skillrq = 5


@unique
class ModDomain(IntEnum):
    """Contains possible modifier domains.

    Used during attribute calculation.
    """
    self = 1  # Self, i.e. item modification source belongs to
    character = 2
    ship = 3
    target = 4
    other = 5  # Module for charge, charge for module


@unique
class ModOperator(IntEnum):
    """Contains possible modifier operator types.

    Used during attribute calculation. Must be ordered in this way to preserve
    operator precedence.
    """
    pre_assign = 1
    pre_mul = 2
    pre_div = 3
    mod_add = 4
    mod_sub = 5
    post_mul = 6
    post_mul_immune = 7  # Eos-specific, immune to penalization
    post_div = 8
    post_percent = 9
    post_assign = 10


@unique
class ModAggregateMode(IntEnum):
    """Contains possible modifier aggregate modes.

    Used during attribute calculation.
    """
    stack = 1
    minimum = 2
    maximum = 3


@unique
class Restriction(IntEnum):
    """Contains possible restriction types.

    Used for fit validation.
    """
    cpu = 1
    powergrid = 2
    calibration = 3
    dronebay_volume = 4
    drone_bandwidth = 5
    launched_drone = 6
    drone_group = 7
    high_slot = 8
    mid_slot = 9
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
    item_class = 26
    state = 27
    charge_group = 28
    charge_size = 29
    charge_volume = 30
    fighter_squad = 31
    fighter_squad_support = 32
    fighter_squad_light = 33
    fighter_squad_heavy = 34
    loaded_item = 35


@unique
class EosTypeId(IntEnum):
    """Contains Eos-specific item type IDs.

    Any values defined here must not overlap with regular item type IDs.
    """
    current_self = -1


@unique
class EosEffectId(IntEnum):
    """Contains Eos-specific effect IDs.

    Any values defined here must not overlap with regular effect IDs.
    """
    char_missile_dmg = -1
    ancillary_paste_armor_rep_boost = -2
