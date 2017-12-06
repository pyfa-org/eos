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


from eos.const.eve import AttrId
from eos.fit.helper import DmgTypes
from eos.fit.helper import TankingLayers
from eos.fit.helper import TankingLayersTotal
from eos.util.volatile_cache import CooperativeVolatileMixin
from eos.util.volatile_cache import volatile_property
from .base import BaseItemMixin


class BufferTankingMixin(BaseItemMixin, CooperativeVolatileMixin):
    """Supports various stats related to buffer tanking."""

    @volatile_property
    def hp(self):
        """Fetch HP stats of the item.

        Returns:
            TankingLayersTotal helper container instance.
        """
        hull = self.attrs.get(AttrId.hp, None)
        armor = self.attrs.get(AttrId.armor_hp, None)
        shield = self.attrs.get(AttrId.shield_capacity, None)
        return TankingLayersTotal(hull, armor, shield)

    @volatile_property
    def resists(self):
        """Fetch resistances of the item.

        Returns:
            TankingLayers helper container instance, whose attributes are
            DmgTypes helper container instances.
        """
        hull = DmgTypes(
            self.__get_resist_by_attr(AttrId.em_dmg_resonance),
            self.__get_resist_by_attr(AttrId.thermal_dmg_resonance),
            self.__get_resist_by_attr(AttrId.kinetic_dmg_resonance),
            self.__get_resist_by_attr(AttrId.explosive_dmg_resonance))
        armor = DmgTypes(
            self.__get_resist_by_attr(AttrId.armor_em_dmg_resonance),
            self.__get_resist_by_attr(AttrId.armor_thermal_dmg_resonance),
            self.__get_resist_by_attr(AttrId.armor_kinetic_dmg_resonance),
            self.__get_resist_by_attr(AttrId.armor_explosive_dmg_resonance))
        shield = DmgTypes(
            self.__get_resist_by_attr(AttrId.shield_em_dmg_resonance),
            self.__get_resist_by_attr(AttrId.shield_thermal_dmg_resonance),
            self.__get_resist_by_attr(AttrId.shield_kinetic_dmg_resonance),
            self.__get_resist_by_attr(AttrId.shield_explosive_dmg_resonance))
        return TankingLayers(hull, armor, shield)

    def __get_resist_by_attr(self, attr_id):
        """Get resistance by attribute ID."""
        try:
            resonance = self.attrs[attr_id]
        except KeyError:
            return None
        else:
            return 1 - resonance

    def get_ehp(self, dmg_profile=None):
        """Get effective HP of an item against passed damage profile.

        Args:
            dmg_profile (optional): DmgProfile helper container instance. If not
                specified, default on-fit damage profile is used.

        Returns:
            TankingLayersTotal helper container instance.
        """
        if dmg_profile is None:
            dmg_profile = self._fit.default_incoming_dmg
        # If damage profile is not specified anywhere, return Nones
        if dmg_profile is None:
            return TankingLayersTotal(None, None, None)
        hull_ehp = self.__get_layer_ehp(
            self.hp.hull, self.resists.hull, dmg_profile)
        armor_ehp = self.__get_layer_ehp(
            self.hp.armor, self.resists.armor, dmg_profile)
        shield_ehp = self.__get_layer_ehp(
            self.hp.shield, self.resists.shield, dmg_profile)
        return TankingLayersTotal(hull_ehp, armor_ehp, shield_ehp)

    def __get_layer_ehp(self, layer_hp, layer_resists, dmg_profile):
        """Calculate layer EHP according to passed data.

        If layer raw HP is None, None is returned.
        """
        if not layer_hp:
            return layer_hp
        tank_mult = self.__get_tanking_efficiency(dmg_profile, layer_resists)
        return layer_hp * tank_mult

    def __get_tanking_efficiency(self, dmg_profile, resists):
        """Get tanking efficiency for passed damage/resistance profiles.

        If any of layer resistances are not specified, they're assumed to be 0.
        """
        dealt = (
            dmg_profile.em + dmg_profile.thermal +
            dmg_profile.kinetic + dmg_profile.explosive)
        absorbed = (
            dmg_profile.em * (resists.em or 0) +
            dmg_profile.thermal * (resists.thermal or 0) +
            dmg_profile.kinetic * (resists.kinetic or 0) +
            dmg_profile.explosive * (resists.explosive or 0))
        received = dealt - absorbed
        return dealt / received

    @volatile_property
    def worst_case_ehp(self):
        """Get eve-style effective HP for the item.

        Eve takes the worst resistance and calculates EHP against it, on a per-
        layer basis.

        Returns:
            TankingLayersTotal helper container instance.
        """
        hull_ehp = self.__get_layer_worst_case_ehp(
            self.hp.hull, self.resists.hull)
        armor_ehp = self.__get_layer_worst_case_ehp(
            self.hp.armor, self.resists.armor)
        shield_ehp = self.__get_layer_worst_case_ehp(
            self.hp.shield, self.resists.shield)
        return TankingLayersTotal(hull_ehp, armor_ehp, shield_ehp)

    def __get_layer_worst_case_ehp(self, layer_hp, layer_resists):
        """Calculate layer EHP according to passed data.

        If layer raw HP is None, None is returned.
        """
        if not layer_hp:
            return layer_hp
        resist = min(
            layer_resists.em or 0,
            layer_resists.thermal or 0,
            layer_resists.kinetic or 0,
            layer_resists.explosive or 0)
        return layer_hp / (1 - resist)
