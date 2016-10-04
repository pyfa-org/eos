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
    """Slot types item can take"""
    module_high = 1
    module_med = 2
    module_low = 3
    rig = 4
    subsystem = 5
    turret = 6
    launcher = 7


# Class used by Modifiers and Item definitions
@unique
class Domain(IntEnum):
    """
    Domain specification. Some legacy code (like old way
    to define modifiers, via expression trees) sometimes
    refer to it using 'location' term.

    Some values are relative, thus item context must be taken
    into account. Used only internally by Info class, item
    classes and calculation engine in general.
    """
    # Self, i.e. carrier of modification source
    self_ = 1
    character = 2
    ship = 3
    # Currently locked and selected target
    target = 4
    # If used from charge, refers charge's container,
    # if used from container, refers its charge
    other = 5
    # No detailed data about this one, according to expressions,
    # it affects everything on grid (the only expression using it
    # is area-of-effect repair, but it's not assigned to any effects)
    area = 6
    # Target stuff in space (e.g. your launched drones and missiles);
    # this domain is Eos-specific and not taken from EVE
    space = 7


@unique
class EffectBuildStatus(IntEnum):
    """
    Statuses which indicate effect->modifiers conversion result,
    part of public API.
    """
    not_built = 1
    # Errors occurred during expression trees parsing or validation
    error = 2
    # Modifiers were generated, but some of elements were dropped as unsupported
    ok_partial = 3
    ok_full = 4


@unique
class Scope(IntEnum):
    """
    Describes when modification is applied, used only internally
    by Modifier class and classes interacting with it
    """
    # Fit-local modification
    local = 1
    # Gang-wide modification
    gang = 2
    # Modification which is applied to target only when modifier
    # carrier is projected# onto it
    projected = 3


@unique
class FilterType(IntEnum):
    """
    Filter type ID holder, used only internally
    by Modifier class and classes interacting with it
    """
    # Affects all items in target domain
    all_ = 1
    # Affects items in target domain with additional filter by group
    group = 2
    # Affects items in target domain with additional filter by skill
    # requirement
    skill = 3
    # Same as skill, but instead of specifying typeID of skill in filter
    # value always refers typeID of carrier
    skill_self = 4


@unique
class Operator(IntEnum):
    """
    Operator ID holder, used only internally
    by Modifier class and classes interacting with it
    """
    # Following operators are used in modifications
    # applied over some duration. We can deliberately assign
    # these some ID, but we need to make sure their IDs are
    # sorted in the order they're kept here for proper
    # attribute calculation process
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
    """
    Fitting restriction types.
    """
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
