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
from eos.stats_container import ItemHP
from eos.stats_container import ResistProfile
from eos.stats_container import TankingLayers
from .base import BaseItemMixin


class BufferTankingMixin(BaseItemMixin):
    """Supports various stats related to buffer tanking."""

    @property
    def hp(self):
        """Fetch HP stats of the item.

        Returns:
            TankingLayersTotal helper container instance.
        """
        hull = self.attrs.get(AttrId.hp, 0)
        armor = self.attrs.get(AttrId.armor_hp, 0)
        shield = self.attrs.get(AttrId.shield_capacity, 0)
        return ItemHP(hull, armor, shield)

    @property
    def resists(self):
        """Fetch resistances of the item.

        Returns:
            TankingLayers helper container instance, whose attributes are
            DmgTypes helper container instances.
        """
        hull = ResistProfile(
            self.__get_resist_by_attr(AttrId.em_dmg_resonance),
            self.__get_resist_by_attr(AttrId.therm_dmg_resonance),
            self.__get_resist_by_attr(AttrId.kin_dmg_resonance),
            self.__get_resist_by_attr(AttrId.expl_dmg_resonance))
        armor = ResistProfile(
            self.__get_resist_by_attr(AttrId.armor_em_dmg_resonance),
            self.__get_resist_by_attr(AttrId.armor_therm_dmg_resonance),
            self.__get_resist_by_attr(AttrId.armor_kin_dmg_resonance),
            self.__get_resist_by_attr(AttrId.armor_expl_dmg_resonance))
        shield = ResistProfile(
            self.__get_resist_by_attr(AttrId.shield_em_dmg_resonance),
            self.__get_resist_by_attr(AttrId.shield_therm_dmg_resonance),
            self.__get_resist_by_attr(AttrId.shield_kin_dmg_resonance),
            self.__get_resist_by_attr(AttrId.shield_expl_dmg_resonance))
        return TankingLayers(hull, armor, shield)

    def __get_resist_by_attr(self, attr_id):
        """Get resistance by attribute ID."""
        return 1 - self.attrs.get(attr_id, 1)

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
            return ItemHP(0, 0, 0)
        hull_ehp = self.__get_layer_ehp(
            self.hp.hull, self.resists.hull, dmg_profile)
        armor_ehp = self.__get_layer_ehp(
            self.hp.armor, self.resists.armor, dmg_profile)
        shield_ehp = self.__get_layer_ehp(
            self.hp.shield, self.resists.shield, dmg_profile)
        return ItemHP(hull_ehp, armor_ehp, shield_ehp)

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
            dmg_profile.em +
            dmg_profile.thermal +
            dmg_profile.kinetic +
            dmg_profile.explosive)
        absorbed = (
            dmg_profile.em * resists.em +
            dmg_profile.thermal * resists.thermal +
            dmg_profile.kinetic * resists.kinetic +
            dmg_profile.explosive * resists.explosive)
        received = dealt - absorbed
        return dealt / received

    @property
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
        return ItemHP(hull_ehp, armor_ehp, shield_ehp)

    def __get_layer_worst_case_ehp(self, layer_hp, layer_resists):
        """Calculate layer EHP according to passed data.

        If layer raw HP is None, None is returned.
        """
        if not layer_hp:
            return layer_hp
        resist = min(
            layer_resists.em,
            layer_resists.thermal,
            layer_resists.kinetic,
            layer_resists.explosive)
        return layer_hp / (1 - resist)
