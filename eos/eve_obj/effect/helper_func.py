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
This module contains functions used by multiple effects, which cannot be
categorized to fit into effect class hierarchy.
"""


import math

from eos.const.eve import AttrId
from eos.util.float import float_to_int


def get_cycles_until_reload_generic(item):
    """Get cycles until reload for items with regular charge mechanics."""
    charge_quantity = item.charge_quantity
    charge_rate = item.attrs.get(AttrId.charge_rate)
    if not charge_rate or charge_quantity is None:
        return None
    cycles = charge_quantity // int(charge_rate)
    if cycles == 0:
        return None
    return cycles


def get_cycles_until_reload_crystal(item):
    """Get cycles until reload for items which use crystals as charge."""
    charge_quantity = item.charge_quantity
    # If item cannot fit any charges, effect cannot cycle
    if not charge_quantity:
        return None
    charge = item.charge
    # Non-damageable crystals can cycle infinitely
    if not charge.attrs.get(AttrId.crystals_get_damaged):
        return math.inf
    # Damageable crystals must have all damage-related stats to calculate how
    # many times they can cycle
    try:
        hp = charge.attrs[AttrId.hp]
        chance = charge.attrs[AttrId.crystal_volatility_chance]
        dmg = charge.attrs[AttrId.crystal_volatility_dmg]
    except KeyError:
        return None
    if hp <= 0:
        return None
    if chance <= 0 or dmg <= 0:
        return math.inf
    cycles = float_to_int(hp / dmg / chance) * charge_quantity
    if cycles == 0:
        return None
    return cycles
