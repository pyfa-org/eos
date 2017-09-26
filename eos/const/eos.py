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
class EffectRunMode(IntEnum):
    """
    Run mode defines under which conditions effect is run.
    """
    # In this mode rules are different, depending on effect category:
    # - Offline: effects from this category are run when item is in offline+ state,
    # and when they do not have fitting usage chance specified
    # - Online: effects from this category are run when item is in online+ state,
    # and when item has runnable 'online' effect
    # - Active: effects from this category are run when item is in active+ state,
    # and only when effect is default item effect
    # - Overload: effects from this category are run when item is in overload+ state
    eve_compliance = 1
    # Effects in this mode are always run if item's state is high enough to run it
    state_compliance = 2
    # Effects in this mode are always running no matter what
    force_run = 3
    # Effects in this mode are never running no matter what
    force_stop = 4


@unique
class EffectBuildStatus(IntEnum):
    skipped = 1
    error = 2
    success_partial = 3
    success = 4
    custom = 5


@unique
class ModifierTargetFilter(IntEnum):
    item = 1
    domain = 2  # Domain children only, excluding parent item
    domain_group = 3  # Domain children only, excluding parent item
    domain_skillrq = 4  # Domain children only, excluding parent item
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
    post_mul_immune = 7  # Immune to penalization
    post_div = 8
    post_percent = 9
    post_assign = 10


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
    item_class = 26
    state = 27
    charge_group = 28
    charge_size = 29
    charge_volume = 30
    booster_effect = 31


@unique
class EosType(IntEnum):
    """
    Container for Eos-specific type IDs. Any values defined
    here must not overlap with regular eve type IDs.
    """
    current_self = -1


@unique
class EosEffect(IntEnum):
    """
    Container for Eos-specific effect IDs. Any values defined
    here must not overlap with regular eve effect IDs.
    """
    char_missile_dmg = -1
