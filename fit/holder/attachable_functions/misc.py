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


def set_state(holder, new_state):
    """
    Used by:
    Drone, Module
    """
    if new_state == holder.state:
        return
    # When holder is assigned to some fit, ask fit to perform
    # fit-specific state switch of our holder
    fit = holder._fit
    if fit is not None:
        fit._holder_state_switch(holder, new_state)
    holder._state = new_state


def _get_item_specific_attr(holder, attr_name):
    """
    If attribute ID which we're trying to get is
    located on holder's item, this functions helps
    to fetch it.
    """
    attr_id = getattr(holder.item, attr_name, None)
    if attr_id is None:
        return None
    try:
        return holder.attributes[attr_id]
    except KeyError:
        return None


def get_tracking_speed(holder):
    """
    Used by:
    Drone, Module
    """
    return _get_item_specific_attr(holder, '_tracking_speed_attribute_id')


def get_optimal_range(holder):
    """
    Used by:
    Drone, Module
    """
    return _get_item_specific_attr(holder, '_range_attribute_id')


def get_falloff_range(holder):
    """
    Used by:
    Drone, Module
    """
    return _get_item_specific_attr(holder, '_falloff_attribute_id')


def get_cycle_time(holder):
    """
    Used by:
    Drone, Module
    """
    return _get_item_specific_attr(holder, '_duration_attribute_id')

