# ==============================================================================
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
# ==============================================================================


__all__ = [
    'turret_filter',
    'missile_filter',
    'drone_filter',
    'sentry_drone_filter'
]


from eos.const.eve import EffectId, TypeId
from eos.fit.item import Drone


def turret_filter(item):
    """True for item which occupies turret hardpoint."""
    if EffectId.turret_fitted in item._running_effect_ids:
        return True
    else:
        return False


def missile_filter(item):
    """True for item which occupies launcher hardpoint."""
    if EffectId.launcher_fitted in item._running_effect_ids:
        return True
    else:
        return False


def drone_filter(item):
    """True for Drone instance."""
    return isinstance(item, Drone)


def sentry_drone_filter(item):
    """True for drone which requires sentry interfacing skill."""
    if not drone_filter(item):
        return False
    try:
        skillrqs = item._type.required_skills
    except AttributeError:
        return False
    if TypeId.sentry_drone_interfacing in skillrqs:
        return True
    else:
        return False
