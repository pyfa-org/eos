# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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


from eos.const.eve import Attribute, Effect
from eos.fit.holder.container import HolderDescriptorOnHolder
from eos.fit.holder.item import Charge
from eos.util.override import OverrideDescriptor
from eos.util.volatile_cache import CooperativeVolatileMixin, VolatileProperty


def _float_to_int(value):
    """
    Function which rounds and ceils value, written to negate
    float representation inaccuracies, (e.g. to have 2.3 / 0.1
    at 23, not 22)
    """
    return int(round(value, 9))


class ChargeableMixin(CooperativeVolatileMixin):
    """
    Mixin intended to use with holders which can have charge loaded
    into them.

    Required arguments:
    charge -- charge to be loaded into holder

    Cooperative methods:
    __init__
    """

    def __init__(self, charge, **kwargs):
        super().__init__(**kwargs)
        self.charge = charge

    charge = HolderDescriptorOnHolder('_charge', 'container', Charge)

    @VolatileProperty
    def charge_quantity_max(self):
        """
        Return max quantity of loadable charges as integer, based
        on the container capacity and charge volume. If any of these
        is not defined, or no charge is found in holder, None is returned.
        """
        if self.charge is None:
            return None
        container_capacity = self.attributes.get(Attribute.capacity)
        charge_volume = self.charge.attributes.get(Attribute.volume)
        if container_capacity is None or charge_volume is None:
            return None
        charges = _float_to_int(container_capacity / charge_volume)
        return charges

    charge_quantity = OverrideDescriptor('charge_quantity_max', class_check=int)

    @VolatileProperty
    def fully_charged_cycles_max(self):
        return self.__get_fully_charged_cycles(self.charge_quantity_max)

    @VolatileProperty
    def fully_charged_cycles(self):
        return self.__get_fully_charged_cycles(self.charge_quantity)

    def __get_fully_charged_cycles(self, charge_quantity):
        """
        Return amount of cycles this container can run until charges are
        depleted. If amount of cycles can vary, mean value if taken
        (t2 laser ammo). Cycles, when amount of charges consumed per
        cycle is more than left in container, are ignored (possible with
        ancillary armor repairers). None is returned if container can
        cycle without ammo consumption.

        Required arguments:
        charge_quantity -- run calculations against this amount of charges
        """
        # Various types of items consume charges during cycle,
        # detect them based on presence of charge_rate attribute
        # in original item (modified attribute value is always
        # possible to fetch, as it has base value, so it's not
        # reliable way to detect it)
        holder_item = self.item
        try:
            item_attribs = holder_item.attributes
        except AttributeError:
            pass
        else:
            if Attribute.charge_rate in item_attribs:
                return self.__get_ammo_full_cycles(charge_quantity)
        # Detect crystal-based items using effects
        try:
            defeff_id = holder_item.default_effect.id
        except AttributeError:
            defeff_id = None
        if defeff_id in (Effect.target_attack, Effect.mining_laser):
            return self.__get_crystal_mean_cycles(charge_quantity)
        return None

    def __get_ammo_full_cycles(self, charge_quantity):
        charge_rate = self.attributes.get(Attribute.charge_rate)
        if not charge_rate or charge_quantity is None:
            return None
        cycles = charge_quantity // int(charge_rate)
        return cycles

    def __get_crystal_mean_cycles(self, charge_quantity):
        charge_attribs = self.charge.attributes
        damageable = charge_attribs.get(Attribute.crystals_get_damaged)
        hp = charge_attribs.get(Attribute.hp)
        chance = charge_attribs.get(Attribute.crystal_volatility_chance)
        damage = charge_attribs.get(Attribute.crystal_volatility_damage)
        if (
            not damageable or
            hp is None or chance is None or
            damage is None or
            charge_quantity is None
        ):
            return None
        cycles = _float_to_int(hp / damage / chance) * charge_quantity
        return cycles

    @VolatileProperty
    def reload_time(self):
        """
        Return holder reload time in seconds.
        """
        # Return hardcoded 1.0 if holder's item has target_attack effect
        # (various lasers), else fetch reload time attribute from holder
        holder_item = self.item
        try:
            defeff_id = holder_item.default_effect.id
        except AttributeError:
            pass
        else:
            if defeff_id in (Effect.target_attack, Effect.mining_laser):
                return 1.0
        reload_ms = self.attributes.get(Attribute.reload_time)
        if reload_ms is None:
            return None
        return reload_ms / 1000
