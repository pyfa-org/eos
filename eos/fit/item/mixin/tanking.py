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


from eos.const.eve import Attribute
from eos.fit.tuples import TankingLayers, TankingLayersTotal, DamageTypes
from eos.util.volatile_cache import CooperativeVolatileMixin, VolatileProperty
from .holder.holder import HolderBase


class BufferTankingMixin(HolderBase, CooperativeVolatileMixin):
    """
    Mixin intended to use with all entities which are able
    to sustain damage (ships, drones, maybe some charges).
    """

    @VolatileProperty
    def hp(self):
        """
        Access point to fetch hp of item. Provides following data:

        .hull, .armor, .shield -- number, or None if data can't
        .total -- total amount of HP, if data for
        some layer is not available, defaults hp of this layer to 0
        """
        hull = self.attributes.get(Attribute.hp, None)
        armor = self.attributes.get(Attribute.armor_hp, None)
        shield = self.attributes.get(Attribute.shield_capacity, None)
        total = (hull or 0) + (armor or 0) + (shield or 0)
        if total == 0 and hull is None and armor is None and shield is None:
            total = None
        return TankingLayersTotal(hull=hull, armor=armor, shield=shield, total=total)

    @VolatileProperty
    def resistances(self):
        """
        Access point to fetch resistances of item. Provides following data:
        .hull.em, .hull.thermal, .hull.kinetic, .hull.explosive,
        .armor.em, .armor.thermal, .armor.kinetic, .armor.explosive,
        .shield.em, .shield.thermal, .shield.kinetic, .shield.explosive
        When resistance data can't be fetched, returns None for requested
        resistance.
        """
        hull = DamageTypes(
            em=self.__get_resistance_by_attr(Attribute.em_damage_resonance),
            thermal=self.__get_resistance_by_attr(Attribute.thermal_damage_resonance),
            kinetic=self.__get_resistance_by_attr(Attribute.kinetic_damage_resonance),
            explosive=self.__get_resistance_by_attr(Attribute.explosive_damage_resonance)
        )
        armor = DamageTypes(
            em=self.__get_resistance_by_attr(Attribute.armor_em_damage_resonance),
            thermal=self.__get_resistance_by_attr(Attribute.armor_thermal_damage_resonance),
            kinetic=self.__get_resistance_by_attr(Attribute.armor_kinetic_damage_resonance),
            explosive=self.__get_resistance_by_attr(Attribute.armor_explosive_damage_resonance)
        )
        shield = DamageTypes(
            em=self.__get_resistance_by_attr(Attribute.shield_em_damage_resonance),
            thermal=self.__get_resistance_by_attr(Attribute.shield_thermal_damage_resonance),
            kinetic=self.__get_resistance_by_attr(Attribute.shield_kinetic_damage_resonance),
            explosive=self.__get_resistance_by_attr(Attribute.shield_explosive_damage_resonance)
        )
        return TankingLayers(hull=hull, armor=armor, shield=shield)

    def __get_resistance_by_attr(self, attr):
        """
        Get resonance by attribute ID and if there's any
        value, convert it to resistance.
        """
        try:
            resonance = self.attributes[attr]
        except KeyError:
            return None
        else:
            return 1 - resonance

    def get_ehp(self, damage_profile):
        """
        Get effective HP of item against passed damage profile.

        Required arguments:
        damage_profile -- object which has numbers as its following attibutes:
        em, thermal, kinetic and explosive

        Object with following attributes is returned:
        .hull, .armor, .shield -- number, or None if HP for layer can't be fetched
        .total -- total effective HP, if data for some layer is not available,
        defaults effective hp of this layer to 0; if data for all layers is not
        available, equals None.
        """
        if (
            damage_profile.em == 0 and
            damage_profile.thermal == 0 and
            damage_profile.kinetic == 0 and
            damage_profile.explosive == 0
        ):
            raise ValueError('damage profile cannot have all damage components as 0')
        hull_ehp = self.__get_layer_ehp(self.hp.hull, self.resistances.hull, damage_profile)
        armor_ehp = self.__get_layer_ehp(self.hp.armor, self.resistances.armor, damage_profile)
        shield_ehp = self.__get_layer_ehp(self.hp.shield, self.resistances.shield, damage_profile)
        total_ehp = (hull_ehp or 0) + (armor_ehp or 0) + (shield_ehp or 0)
        if total_ehp == 0 and hull_ehp is None and armor_ehp is None and shield_ehp is None:
            total_ehp = None
        return TankingLayersTotal(hull=hull_ehp, armor=armor_ehp, shield=shield_ehp, total=total_ehp)

    def __get_layer_ehp(self, layer_hp, layer_resists, damage_profile):
        """
        Calculate layer EHP according to passed data.

        If layer raw HP is None, None is returned
        """
        if not layer_hp:
            return layer_hp
        return layer_hp * self.__get_tanking_efficiency(damage_profile, layer_resists)

    def __get_tanking_efficiency(self, dmg, res):
        """
        Get tanking efficiency for passed damage/resistance
        profiles.

        If any of layer resistances are not specified,
        they're assumed to be 0.
        """
        dealt = dmg.em + dmg.thermal + dmg.kinetic + dmg.explosive
        absorbed = (
            dmg.em * (res.em or 0) +
            dmg.thermal * (res.thermal or 0) +
            dmg.kinetic * (res.kinetic or 0) +
            dmg.explosive * (res.explosive or 0)
        )
        received = dealt - absorbed
        return dealt / received

    @VolatileProperty
    def worst_case_ehp(self):
        """
        Get EVE-style effective HP for item.

        EVE takes the worst resistance and calculates EHP against it,
        on a per-layer basis.

        Object with following attributes is returned:
        .hull, .armor, .shield -- number, or None if HP for layer can't be fetched
        .total -- total effective HP, if data for some layer is not available,
        defaults effective hp of this layer to 0; if data for all layers is not
        available, equals None.
        """
        hull_ehp = self.__get_layer_worst_case_ehp(self.hp.hull, self.resistances.hull)
        armor_ehp = self.__get_layer_worst_case_ehp(self.hp.armor, self.resistances.armor)
        shield_ehp = self.__get_layer_worst_case_ehp(self.hp.shield, self.resistances.shield)
        total_ehp = (hull_ehp or 0) + (armor_ehp or 0) + (shield_ehp or 0)
        if total_ehp == 0 and hull_ehp is None and armor_ehp is None and shield_ehp is None:
            total_ehp = None
        return TankingLayersTotal(hull=hull_ehp, armor=armor_ehp, shield=shield_ehp, total=total_ehp)

    def __get_layer_worst_case_ehp(self, layer_hp, layer_resists):
        """
        Calculate layer EHP according to passed data.

        If layer raw HP is None, None is returned
        """
        if not layer_hp:
            return layer_hp
        resistance = min(
            layer_resists.em or 0,
            layer_resists.thermal or 0,
            layer_resists.kinetic or 0,
            layer_resists.explosive or 0
        )
        return layer_hp / (1 - resistance)
