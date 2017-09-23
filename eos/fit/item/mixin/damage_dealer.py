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


from enum import IntEnum, unique

from eos.const.eve import Attribute, Effect
from eos.fit.helper import DamageTypesTotal
from eos.util.volatile_cache import CooperativeVolatileMixin, volatile_property
from .base import BaseItemMixin
from .defeff_proxy import DefaultEffectProxyMixin


@unique
class WeaponType(IntEnum):
    # Everything turret-based, including drones
    turret = 1
    # All regular missiles
    guided_missile = 2
    # TODO: instant missile was assigned just to fighter bombers
    # Fighter-bomber missiles
    instant_missile = 3
    # Free-aiming bombs, launched towards ship vector
    bomb = 4
    # Damage done to single target
    direct = 5
    # Smartbombs
    untargeted_aoe = 6


BASIC_EFFECT_WEAPON_MAP = {
    Effect.target_attack: WeaponType.turret,
    Effect.projectile_fired: WeaponType.turret,
    Effect.emp_wave: WeaponType.untargeted_aoe,
    # TODO: instant missile was assigned just to fighter bombers
    Effect.fighter_missile: WeaponType.instant_missile,
    Effect.super_weapon_amarr: WeaponType.direct,
    Effect.super_weapon_caldari: WeaponType.direct,
    Effect.super_weapon_gallente: WeaponType.direct,
    Effect.super_weapon_minmatar: WeaponType.direct
}

CHARGE_EFFECT_WEAPON_MAP = {
    Effect.use_missiles: {
        Effect.missile_launching: WeaponType.guided_missile,
        Effect.fof_missile_launching: WeaponType.guided_missile,
        Effect.bomb_launching: WeaponType.bomb
    }
}


class DamageDealerMixin(DefaultEffectProxyMixin, BaseItemMixin, CooperativeVolatileMixin):
    """
    Mixin intended to use with all entities which are able
    to deal damage (modules, drones).
    """

    @volatile_property
    def _pereff_weapon_types(self):
        """
        Get weapon types of the item. Weapon types defines mechanics used
        to deliver damage and attributes used for damage calculation on a
        per-effect basis. If item is not a weapon or an inactive weapon,
        empty dictionary is returned.
        """
        # Format: {effect ID: weapon type}
        weapon_types = {}
        # If item contains some charge type but can't hold enough to actually
        # cycle itself, do not consider such item as weapon
        if getattr(self, 'charged_cycles', None) == 0:
            return weapon_types
        for effect_id in self._active_effects:
            # Weapon properties are defined by item effects
            if effect_id in BASIC_EFFECT_WEAPON_MAP:
                weapon_types[effect_id] = BASIC_EFFECT_WEAPON_MAP[effect_id]
            # For missiles and bombs, we need to use charge default effect as well
            # as it defines property of 'projectile' which massively influence type
            # of weapon
            elif effect_id in CHARGE_EFFECT_WEAPON_MAP:
                charge = getattr(self, 'charge', None)
                try:
                    charge_defeff_id = charge._eve_type.default_effect.id
                except AttributeError:
                    continue
                if charge_defeff_id not in charge._active_effects:
                    continue
                try:
                    weapon_types[effect_id] = CHARGE_EFFECT_WEAPON_MAP[effect_id][charge_defeff_id]
                except KeyError:
                    continue
        return weapon_types

    def __get_volley_self(self):
        """
        Return item damage attribs as 4-tuple.
        """
        return self.__get_volley_item(self)

    def __get_volley_charge(self):
        """
        Return item's charge damage attribs as 4-tuple.
        """
        charge = getattr(self, 'charge', None)
        if charge is None:
            return None, None, None, None
        return self.__get_volley_item(charge)

    def __get_volley_hybrid(self):
        """
        If charge is loaded, return damage attribs, if not -
         item attribs.
        """
        charge = getattr(self, 'charge', None)
        if charge is not None:
            return self.__get_volley_item(charge)
        else:
            return self.__get_volley_item(self)

    def __get_volley_item(self, item):
        """
        Get damage per type as tuple for passed item.
        """
        em = item.attributes.get(Attribute.em_damage)
        therm = item.attributes.get(Attribute.thermal_damage)
        kin = item.attributes.get(Attribute.kinetic_damage)
        expl = item.attributes.get(Attribute.explosive_damage)
        return em, therm, kin, expl

    # Format: {weapon type: (function which fetches base damage, damage multiplier flag)}
    __volley_fetchers = {
        WeaponType.turret: (__get_volley_hybrid, True),
        WeaponType.guided_missile: (__get_volley_charge, False),
        WeaponType.instant_missile: (__get_volley_self, True),
        WeaponType.bomb: (__get_volley_charge, False),
        WeaponType.direct: (__get_volley_self, False),
        WeaponType.untargeted_aoe: (__get_volley_self, False)
    }

    @volatile_property
    def _pereff_volleys(self):
        """
        Return base volleys for all damage-dealing effects of the current item;
        values returned are nominal volleys, not modified by any resistances.
        """
        # Format: {effect ID: base volley}
        base_volleys = {}
        for effect_id, weapon_type in self._pereff_weapon_types.items():
            volley_fetcher, multiply = self.__volley_fetchers[weapon_type]
            em, therm, kin, expl = volley_fetcher(self)
            if multiply:
                try:
                    multiplier = self.attributes[Attribute.damage_multiplier]
                except KeyError:
                    pass
                else:
                    # Guards against None-values
                    try:
                        em *= multiplier
                    except TypeError:
                        pass
                    try:
                        therm *= multiplier
                    except TypeError:
                        pass
                    try:
                        kin *= multiplier
                    except TypeError:
                        pass
                    try:
                        expl *= multiplier
                    except TypeError:
                        pass
            base_volleys[effect_id] = DamageTypesTotal(em=em, thermal=therm, kinetic=kin, explosive=expl)
        return base_volleys

    def get_nominal_volley(self, target_resistances=None):
        """
        Get nominal volley for item, calculated against passed
        target resistances.

        Optional arguments:
        target_resistances -- object which has following numbers as its attibutes:
        em, thermal, kinetic and explosive (all in range [0, 1])
        If none, raw volley damage is calculated. By default None.

        Return value:
        Object with volley damage of current item, accessible via following attributes:
        em, thermal, kinetic, explosive, total
        """
        # TODO: Combine multiple volleys into one as temporary measure
        em, therm, kin, expl = None, None, None, None
        for volley in self._pereff_volleys.values():
            if em is None:
                em = volley.em
            else:
                try:
                    em += volley.em
                except TypeError:
                    pass
            if therm is None:
                therm = volley.thermal
            else:
                try:
                    therm += volley.thermal
                except TypeError:
                    pass
            if kin is None:
                kin = volley.kinetic
            else:
                try:
                    kin += volley.kinetic
                except TypeError:
                    pass
            if expl is None:
                expl = volley.explosive
            else:
                try:
                    expl += volley.explosive
                except TypeError:
                    pass
        if target_resistances is not None:
            em_resonance = 1 - target_resistances.em
            therm_resonance = 1 - target_resistances.thermal
            kin_resonance = 1 - target_resistances.kinetic
            expl_resonance = 1 - target_resistances.explosive
            # Guards against None-values of volley components
            try:
                em *= em_resonance
            except TypeError:
                em = None
            try:
                therm *= therm_resonance
            except TypeError:
                therm = None
            try:
                kin *= kin_resonance
            except TypeError:
                kin = None
            try:
                expl *= expl_resonance
            except TypeError:
                expl = None
        return DamageTypesTotal(em=em, thermal=therm, kinetic=kin, explosive=expl)

    def get_nominal_dps(self, target_resistances=None, reload=False):
        volley = self.get_nominal_volley(target_resistances=target_resistances)
        # If all attribs of base volley are None, nothing we can do here
        if (volley.total is None and volley.em is None and volley.thermal is None and
                volley.kinetic is None and volley.explosive is None):
            return volley
        cycle_time = self.cycle_time
        # Items may have no reactivation attribute, return None or actual value;
        # make sure we use 0 as fallback in all cases
        reactivation_time = getattr(self, 'reactivation_delay', 0) or 0
        # Time which module should spend on each cycle, regardless of any conditions
        full_cycle_time = cycle_time + reactivation_time
        if reload:
            try:
                reload_time = self.reload_time
                charged_cycles = self.charged_cycles
            except AttributeError:
                pass
            else:
                if reload_time is not None and charged_cycles is not None:
                    # To each cycle, add average time which module should spend reloading
                    # (and take into account that reactivation delay, which we already take
                    # into account, can cover reload time partially or fully)
                    full_cycle_time += max(reload_time - reactivation_time, 0) / charged_cycles
        # Guards against None-valued volley components
        try:
            em = volley.em / full_cycle_time
        except TypeError:
            em = None
        try:
            therm = volley.thermal / full_cycle_time
        except TypeError:
            therm = None
        try:
            kin = volley.kinetic / full_cycle_time
        except TypeError:
            kin = None
        try:
            expl = volley.explosive / full_cycle_time
        except TypeError:
            expl = None
        return DamageTypesTotal(em=em, thermal=therm, kinetic=kin, explosive=expl)

    def get_volley_vs_target(self, target_data=None, target_resistances=None):
        # TODO
        return

    def get_chance_to_hit(self, target_data=None):
        # TODO
        return

    def get_dps_vs_target(self, target_data=None, target_resistances=None, reload=True):
        # TODO
        return
