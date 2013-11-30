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


from eos.const.eve import Attribute, Effect
from eos.fit.tuples import DamageTypesTotal
from eos.util.enum import Enum
from eos.util.volatile_cache import CooperativeVolatileMixin, VolatileProperty
from .holder import HolderBase


class WeaponType(metaclass=Enum):
    # Everything turret-based, including drones
    turret = 1
    # All regular missiles
    guided_missile = 2
    # Fighter-bomber missiles
    instant_missile = 3
    # Free-aiming bombs, launched towards ship vector
    bomb = 4
    # Damage done to single target
    direct = 5
    # Smartbombs
    untargeted_aoe = 6


SIMPLE_EFFECT_WEAPON_MAP = {
    Effect.target_attack: WeaponType.turret,
    Effect.projectile_fired: WeaponType.turret,
    Effect.emp_wave: WeaponType.untargeted_aoe,
    Effect.fighter_missile: WeaponType.instant_missile,
    Effect.super_weapon_amarr: WeaponType.direct,
    Effect.super_weapon_caldari: WeaponType.direct,
    Effect.super_weapon_gallente: WeaponType.direct,
    Effect.super_weapon_minmatar: WeaponType.direct
}

MISSILE_EFFECT_WEAPON_MAP = {
    Effect.missile_launching: WeaponType.guided_missile,
    Effect.fof_missile_launching: WeaponType.guided_missile,
    Effect.bomb_launching: WeaponType.bomb
}


class DamageDealerMixin(HolderBase, CooperativeVolatileMixin):
    """
    Mixin intended to use with all entities which are able
    to deal damage (modules, drones).
    """

    def get_nominal_volley(self, target_resistances=None):
        volley = self._base_volley
        if target_resistances is not None:
            em = volley.em * (1 - target_resistances.em)
            therm = volley.thermal * (1 - target_resistances.thermal)
            kin = volley.kinetic * (1 - target_resistances.kinetic)
            expl = volley.explosive * (1 - target_resistances.explosive)
            total = em + therm + kin + expl
            volley = DamageTypesTotal(em=em, thermal=therm, kinetic=kin, explosive=expl, total=total)
        return volley

    @VolatileProperty
    def _base_volley(self):
        if self._weapon_type == WeaponType.turret:
            charge = getattr(self, 'charge', None)
            if charge is not None:
                em, therm, kin, expl = self.__get_holder_damage(charge)
            else:
                em, therm, kin, expl = self.__get_holder_damage(self)
            try:
                multiplier = self.attributes[Attribute.damage_multiplier]
            except KeyError:
                pass
            else:
                em *= multiplier
                therm *= multiplier
                kin *= multiplier
                expl *= multiplier
            total = em + therm + kin + expl
            volley = DamageTypesTotal(em=em, thermal=therm, kinetic=kin, explosive=expl, total=total)
        else:
            volley = None
        return volley

    def get_volley_vs_target(self, target_data=None, target_resistances=None):
        return

    def get_chance_to_hit(self, target_data=None):
        return

    def get_nominal_dps(self, target_resistances=None, reload=True):
        volley = self.get_nominal_volley(target_resistances=target_resistances)
        cycle = self.cycle_time
        reactivation = getattr(self, 'reactivation_delay', 0)
        if reload:
            try:
                reload_time = self.reload_time
                charged_cycles = self.fully_charged_cycles_max
            except AttributeError:
                mean_cycle_time = cycle + reactivation
            else:
                # Actual additional time which module spends reloading,
                # not on cycling or cooling down reactivation timer
                reload_idle_time = max(reload_time - reactivation, 0)
                mean_cycle_time = cycle + reactivation + (reload_idle_time / charged_cycles)
        else:
            mean_cycle_time = cycle + reactivation
        em = volley.em / mean_cycle_time
        therm = volley.thermal / mean_cycle_time
        kin = volley.kinetic / mean_cycle_time
        expl = volley.explosive / mean_cycle_time
        total = em + therm + kin + expl
        return DamageTypesTotal(em=em, thermal=therm, kinetic=kin, explosive=expl, total=total)

    def get_dps_vs_target(self, target_data=None, target_resistances=None, reload=True):
        return

    @VolatileProperty
    def _weapon_type(self):
        """
        Get weapon type of holder. Weapon type defines mechanics used to
        deliver damage and attributes used for damage calculation. If
        holder is not a weapon or an inactive weapon, None is returned.
        """
        holder_item = self.item
        # Guard against malformed or absent items
        try:
            holder_deffeff = holder_item.default_effect
        except AttributeError:
            return None
        # Guard against malformed or absent default effect
        try:
            holder_defeff_id = holder_deffeff.id
            holder_defeff_state = holder_deffeff._state
        except AttributeError:
            return None
        # Weapon properties are defined by holder default effect;
        # thus, if holder isn't in state to have this effect 'active',
        # it can't be considered as weapon
        if self.state < holder_defeff_state:
            return None
        # For some weapon types, it's enough to use just holder for detection
        weapon_type = SIMPLE_EFFECT_WEAPON_MAP.get(holder_defeff_id)
        if weapon_type is not None:
            return weapon_type
        # For missiles and bombs, we need to use charge as well, as it
        # defines property of 'projectile' which massively influence type
        # of weapon
        if holder_defeff_id == Effect.missile_launching:
            charge = getattr(self, 'charge', None)
            # Guard against malformed or absent item and default effect
            try:
                charge_defeff_id = charge.item.default_effect.id
            except AttributeError:
                charge_defeff_id = None
            try:
                return MISSILE_EFFECT_WEAPON_MAP[charge_defeff_id]
            except KeyError:
                pass
        return None

    def __get_holder_damage(self, holder):
        """
        Get damage per type as tuple for passed holder.
        """
        em = holder.attributes.get(Attribute.em_damage, 0)
        therm = holder.attributes.get(Attribute.thermal_damage, 0)
        kin = holder.attributes.get(Attribute.kinetic_damage, 0)
        expl = holder.attributes.get(Attribute.explosive_damage, 0)
        return em, therm, kin, expl
