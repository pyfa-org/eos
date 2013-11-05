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
from eos.util.volatile_cache import CooperativeVolatileMixin, VolatileProperty


class BufferTankingMixin(CooperativeVolatileMixin):
    """
    Mixin intended to use with all entities which are able
    to sustain damage (ships, drones, maybe some charges).
    """

    @VolatileProperty
    def hp(self):
        hull = self.attributes.get(Attribute.hp, None)
        armor = self.attributes.get(Attribute.armor_hp, None)
        shield = self.attributes.get(Attribute.shield_capacity, None)
        total = (hull or 0) + (armor or 0) + (shield or 0)
        return Hitpoints(hull=hull, armor=armor, shield=shield, total=total)

    @VolatileProperty
    def resistances(self):
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

    def __get_resistance_by_attr(self, attribute):
        """
        Get resonance by attribute ID and if there's any
        value, convert it to resistance.
        """
        try:
            resonance = self.attributes[attribute]
        except KeyError:
            return None
        else:
            return 1 - resonance

    def get_ehp(self, damage_profile):
        hull_ehp = self.__get_layer_ehp(self.hp.hull, self.resistances.hull, damage_profile)
        armor_ehp = self.__get_layer_ehp(self.hp.armor, self.resistances.armor, damage_profile)
        shield_ehp = self.__get_layer_ehp(self.hp.shield, self.resistances.shield, damage_profile)
        total_ehp = (hull_ehp or 0) + (armor_ehp or 0) + (shield_ehp or 0)
        return Hitpoints(hull=hull_ehp, armor=armor_ehp, shield=shield_ehp, total=total_ehp)

    def __get_layer_ehp(self, layer_hp, layer_resistances, damage_profile):
        """
        Calculate layer EHP according to passed data.

        If layer raw HP is None, None is returned
        """
        if not layer_hp:
            return layer_hp
        return layer_hp * self.__get_tanking_efficiency(damage_profile, layer_resistances)

    def __get_tanking_efficiency(self, dmg, res):
        """
        Get tanking efficiency for passed damage/resistance
        profiles.

        If any of layer resistances are not specified,
        they're assumed to be 0.
        """
        dealt = dmg.em + dmg.thermal + dmg.kinetic + dmg.explosive
        absorbed = (dmg.em * (res.em or 0) +
                    dmg.thermal * (res.thermal or 0) +
                    dmg.kinetic * (res.kinetic or 0) +
                    dmg.explosive * (res.explosive or 0))
        received = dealt - absorbed
        return dealt / received

    @VolatileProperty
    def worst_case_ehp(self):
        hull_ehp = self.__get_layer_worst_case_ehp(self.hp.hull, self.resistances.hull)
        armor_ehp = self.__get_layer_worst_case_ehp(self.hp.armor, self.resistances.armor)
        shield_ehp = self.__get_layer_worst_case_ehp(self.hp.shield, self.resistances.shield)
        total_ehp = (hull_ehp or 0) + (armor_ehp or 0) + (shield_ehp or 0)
        return Hitpoints(hull=hull_ehp, armor=armor_ehp, shield=shield_ehp, total=total_ehp)

    def __get_layer_worst_case_ehp(self, layer_hp, layer_resistances):
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
