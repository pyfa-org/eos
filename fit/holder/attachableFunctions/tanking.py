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


def getHp(holder):
    """
    Used by:
    Drone, Ship
    """
    hull = holder.attributes.get(Attribute.hp, None)
    armor = holder.attributes.get(Attribute.armorHp, None)
    shield = holder.attributes.get(Attribute.shieldCapacity, None)
    total = (hull or 0) + (armor or 0) + (shield or 0)
    return Hitpoints(hull=hull, armor=armor, shield=shield, total=total)

def _getResistanceByAttr(holder, attribute):
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

def getResistances(holder):
    """
    Used by:
    Drone, Ship
    """
    hull = DamageTypes(em=_getResistanceByAttr(holder, Attribute.emDamageResonance),
                       thermal=_getResistanceByAttr(holder, Attribute.thermalDamageResonance),
                       kinetic=_getResistanceByAttr(holder, Attribute.kineticDamageResonance),
                       explosive=_getResistanceByAttr(holder, Attribute.explosiveDamageResonance))
    armor = DamageTypes(em=_getResistanceByAttr(holder, Attribute.armorEmDamageResonance),
                        thermal=_getResistanceByAttr(holder, Attribute.armorThermalDamageResonance),
                        kinetic=_getResistanceByAttr(holder, Attribute.armorKineticDamageResonance),
                        explosive=_getResistanceByAttr(holder, Attribute.armorExplosiveDamageResonance))
    shield = DamageTypes(em=_getResistanceByAttr(holder, Attribute.shieldEmDamageResonance),
                         thermal=_getResistanceByAttr(holder, Attribute.shieldThermalDamageResonance),
                         kinetic=_getResistanceByAttr(holder, Attribute.shieldKineticDamageResonance),
                         explosive=_getResistanceByAttr(holder, Attribute.shieldExplosiveDamageResonance))
    return TankingLayers(hull=hull, armor=armor, shield=shield)

def _getTankingEfficiency(dmg, res):
    """
    Get tanking efficiency for passed damage/resistance
    profiles.

    If any of layer resistances are not specified,
    they're assumed to be 0.
    """
    dmgDealt = dmg.em + dmg.thermal + dmg.kinetic + dmg.explosive
    absorbedDmg = (dmg.em * (res.em or 0) +
                   dmg.thermal * (res.thermal or 0) +
                   dmg.kinetic * (res.kinetic or 0) +
                   dmg.explosive * (res.explosive or 0))
    receivedDmg = dmgDealt - absorbedDmg
    return dmgDealt / receivedDmg

def _getLayerEhp(layerHp, layerResistances, damageProfile):
    """
    Calculate layer EHP according to passed data.

    If layer raw HP is None, None is returned
    """
    if not layerHp:
        return layerHp
    return layerHp * _getTankingEfficiency(damageProfile, layerResistances)

def getEhp(holder, damageProfile):
    """
    Used by:
    Drone, Ship
    """
    hullEhp = _getLayerEhp(holder.hp.hull, holder.resistances.hull, damageProfile)
    armorEhp = _getLayerEhp(holder.hp.armor, holder.resistances.armor, damageProfile)
    shieldEhp = _getLayerEhp(holder.hp.shield, holder.resistances.shield, damageProfile)
    totalEhp = (hullEhp or 0) + (armorEhp or 0) + (shieldEhp or 0)
    return Hitpoints(hull=hullEhp, armor=armorEhp, shield=shieldEhp, total=totalEhp)

def _getLayerWorstCaseEhp(layerHp, layerResistances):
    """
    Calculate layer EHP according to passed data.

    If layer raw HP is None, None is returned
    """
    if not layerHp:
        return layerHp
    resistance = min(layerResistances.em or 0,
                     layerResistances.thermal or 0,
                     layerResistances.kinetic or 0,
                     layerResistances.explosive or 0)
    return layerHp / (1 - resistance)

def getWorstCaseEhp(holder):
    """
    Used by:
    Drone, Ship
    """
    hullEhp = _getLayerWorstCaseEhp(holder.hp.hull, holder.resistances.hull)
    armorEhp = _getLayerWorstCaseEhp(holder.hp.armor, holder.resistances.armor)
    shieldEhp = _getLayerWorstCaseEhp(holder.hp.shield, holder.resistances.shield)
    totalEhp = (hullEhp or 0) + (armorEhp or 0) + (shieldEhp or 0)
    return Hitpoints(hull=hullEhp, armor=armorEhp, shield=shieldEhp, total=totalEhp)
