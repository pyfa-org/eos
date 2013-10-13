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


from eos.const.eve import Attribute
from eos.fit.tuples import Hitpoints, TankingLayers, DamageTypes


def get_hp(holder):
    """
    Used by:
    Drone, Ship
    """
    hull = holder.attributes.get(Attribute.hp, None)
    armor = holder.attributes.get(Attribute.armor_hp, None)
    shield = holder.attributes.get(Attribute.shield_capacity, None)
    total = (hull or 0) + (armor or 0) + (shield or 0)
    return Hitpoints(hull=hull, armor=armor, shield=shield, total=total)


def _get_resistance_by_attr(holder, attribute):
    """
    Get resonance by attribute ID and if there's any
    value, convert it to resistance.
    """
    try:
        resonance = holder.attributes[attribute]
    except KeyError:
        return None
    else:
        return 1 - resonance


def get_resistances(holder):
    """
    Used by:
    Drone, Ship
    """
    hull = DamageTypes(
        em=_get_resistance_by_attr(holder, Attribute.em_damage_resonance),
        thermal=_get_resistance_by_attr(holder, Attribute.thermal_damage_resonance),
        kinetic=_get_resistance_by_attr(holder, Attribute.kinetic_damage_resonance),
        explosive=_get_resistance_by_attr(holder, Attribute.explosive_damage_resonance)
    )
    armor = DamageTypes(
        em=_get_resistance_by_attr(holder, Attribute.armor_em_damage_resonance),
        thermal=_get_resistance_by_attr(holder, Attribute.armor_thermal_damage_resonance),
        kinetic=_get_resistance_by_attr(holder, Attribute.armor_kinetic_damage_resonance),
        explosive=_get_resistance_by_attr(holder, Attribute.armor_explosive_damage_resonance)
    )
    shield = DamageTypes(
        em=_get_resistance_by_attr(holder, Attribute.shield_em_damage_resonance),
        thermal=_get_resistance_by_attr(holder, Attribute.shield_thermal_damage_resonance),
        kinetic=_get_resistance_by_attr(holder, Attribute.shield_kinetic_damage_resonance),
        explosive=_get_resistance_by_attr(holder, Attribute.shield_explosive_damage_resonance)
    )
    return TankingLayers(hull=hull, armor=armor, shield=shield)


def _get_tanking_efficiency(dmg, res):
    """
    Get tanking efficiency for passed damage/resistance
    profiles.

    If any of layer resistances are not specified,
    they're assumed to be 0.
    """
    dmg_dealt = dmg.em + dmg.thermal + dmg.kinetic + dmg.explosive
    absorbed_dmg = (dmg.em * (res.em or 0) +
                    dmg.thermal * (res.thermal or 0) +
                    dmg.kinetic * (res.kinetic or 0) +
                    dmg.explosive * (res.explosive or 0))
    received_dmg = dmg_dealt - absorbed_dmg
    return dmg_dealt / received_dmg


def _get_layer_ehp(layer_hp, layer_resistances, damage_profile):
    """
    Calculate layer EHP according to passed data.

    If layer raw HP is None, None is returned
    """
    if not layer_hp:
        return layer_hp
    return layer_hp * _get_tanking_efficiency(damage_profile, layer_resistances)


def get_ehp(holder, damage_profile):
    """
    Used by:
    Drone, Ship
    """
    hull_ehp = _get_layer_ehp(holder.hp.hull, holder.resistances.hull, damage_profile)
    armor_ehp = _get_layer_ehp(holder.hp.armor, holder.resistances.armor, damage_profile)
    shield_ehp = _get_layer_ehp(holder.hp.shield, holder.resistances.shield, damage_profile)
    total_ehp = (hull_ehp or 0) + (armor_ehp or 0) + (shield_ehp or 0)
    return Hitpoints(hull=hull_ehp, armor=armor_ehp, shield=shield_ehp, total=total_ehp)


def _get_layer_worst_case_ehp(layer_hp, layer_resistances):
    """
    Calculate layer EHP according to passed data.

    If layer raw HP is None, None is returned
    """
    if not layer_hp:
        return layer_hp
    resistance = min(layer_resistances.em or 0,
                     layer_resistances.thermal or 0,
                     layer_resistances.kinetic or 0,
                     layer_resistances.explosive or 0)
    return layer_hp / (1 - resistance)


def get_worst_case_ehp(holder):
    """
    Used by:
    Drone, Ship
    """
    hull_ehp = _get_layer_worst_case_ehp(holder.hp.hull, holder.resistances.hull)
    armor_ehp = _get_layer_worst_case_ehp(holder.hp.armor, holder.resistances.armor)
    shield_ehp = _get_layer_worst_case_ehp(holder.hp.shield, holder.resistances.shield)
    total_ehp = (hull_ehp or 0) + (armor_ehp or 0) + (shield_ehp or 0)
    return Hitpoints(hull=hull_ehp, armor=armor_ehp, shield=shield_ehp, total=total_ehp)
