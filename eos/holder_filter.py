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


from eos.const.eve import Type, Group, Category


__all__ = [
    'turret_filter',
    'missile_filter',
    'drone_filter',
    'sentry_drone_filter'
]

TURRET_GROUPS = (Group.projectile_weapon, Group.energy_weapon, Group.hydrid_weapon)
MISSILE_LAUNCHER_GROUPS = (
    Group.missile_launcher_rocket,
    Group.missile_launcher_light,
    Group.missile_launcher_rapid_light,
    Group.missile_launcher_heavy_assault,
    Group.missile_launcher_heavy,
    Group.missile_launcher_rapid_heavy,
    Group.missile_launcher_torpedo,
    Group.missile_launcher_cruise,
    Group.missile_launcher_citadel
)


def turret_filter(holder):
    """
    True for all items belonging to projectile,
    hybrid and energy weapon groups.
    """
    try:
        group = holder.item.group
    except AttributeError:
        return False
    if group in TURRET_GROUPS:
        return True
    else:
        return False


def missile_filter(holder):
    """
    True for all items which belong to various missile
    launcher groups.
    """
    try:
        group = holder.item.group
    except AttributeError:
        return False
    if group in MISSILE_LAUNCHER_GROUPS:
        return True
    else:
        return False


def drone_filter(holder):
    """
    True for all items belonging to drone category.
    """
    try:
        category = holder.item.category
    except AttributeError:
        return False
    if category == Category.drone:
        return True
    else:
        return False


def sentry_drone_filter(holder):
    """
    True for all drones which require sentry interfacing skill.
    """
    if not drone_filter(holder):
        return False
    try:
        skillrqs = holder.item.required_skills
    except AttributeError:
        return False
    if Type.sentry_drone_interfacing in skillrqs:
        return True
    else:
        return False
