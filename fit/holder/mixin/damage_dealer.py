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


from eos.const.eos import WeaponType
from eos.const.eve import Attribute, Effect
from eos.fit.tuples import DamageTypesTotal
from eos.util.volatile_cache import CooperativeVolatileMixin, VolatileProperty
from .holder import HolderBase


class DamageDealerMixin(HolderBase, CooperativeVolatileMixin):
    """
    Mixin intended to use with all entities which are able
    to deal damage (modules, drones).
    """

    def get_nominal_volley(self, target_resistances=None):
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
        holder is not a weapon or inactive weapon, None is returned.
        """
        # For some weapon types, it's enough to use just holder
        # effects for detection
        holder_item = self.item
        try:
            holder_effect_ids = holder_item._effect_ids
        except AttributeError:
            holder_effect_ids = ()
        if (Effect.target_attack in holder_effect_ids or
                Effect.projectile_fired in holder_effect_ids):
            return WeaponType.turret
        if Effect.emp_wave in holder_effect_ids:
            return WeaponType.untargeted_aoe
        if Effect.fighter_missile in holder_effect_ids:
            return WeaponType.instant_missile
        if (Effect.super_weapon_amarr in holder_effect_ids or
                Effect.super_weapon_caldari in holder_effect_ids or
                Effect.super_weapon_gallente in holder_effect_ids or
                Effect.super_weapon_minmatar in holder_effect_ids):
            return WeaponType.direct
        # For missiles and bombs, we need to use charge effect, as it
        # defines property of 'projectile'
        charge = getattr(self, 'charge', None)
        try:
            charge_effect_ids = charge.item._effect_ids
        except AttributeError:
            charge_effect_ids = ()
        if Effect.use_missiles in holder_effect_ids:
            if (Effect.missile_launching in charge_effect_ids or
                    Effect.fof_missile_launching in charge_effect_ids):
                return WeaponType.guided_missile
            if Effect.bomb_launching in charge_effect_ids:
                return WeaponType.bomb
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
