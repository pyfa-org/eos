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


from eos.const.eve import AttributeId, EffectId
from eos.fit.container import ItemDescriptor
from eos.fit.item import Charge
from eos.util.volatile_cache import CooperativeVolatileMixin, volatile_property
from .base import BaseItemMixin


def _float_to_int(value):
    """Convert number to integer, taking care of float errors.

    Without its use float calculation representation may lead to undesirable
    results, e.g. int(2.3 / 0.1) = 22.
    """
    return int(round(value, 9))


class ChargeableMixin(BaseItemMixin, CooperativeVolatileMixin):
    """Supports ability to load charges into items.

    Args:
        charge: Charge to be loaded into item.

    Cooperative methods:
        __init__
    """

    def __init__(self, charge, **kwargs):
        super().__init__(**kwargs)
        self.charge = charge

    charge = ItemDescriptor('_charge', Charge)

    @property
    def _child_items(self):
        return (self.charge,) if self.charge is not None else ()

    @volatile_property
    def charge_quantity(self):
        """Max quantity of loadable charges.

        It depends on capacity of this item and volume of charge.

        Returns: Quantity of loadable charges as integer. If any of necessary
        attribute values is not defined, or no charge is found in item, None is
        returned.
        """
        if self.charge is None:
            return None
        container_capacity = self.attributes.get(AttributeId.capacity)
        charge_volume = self.charge.attributes.get(AttributeId.volume)
        if container_capacity is None or charge_volume is None:
            return None
        charges = _float_to_int(container_capacity / charge_volume)
        return charges

    @volatile_property
    def charged_cycles(self):
        """Quantity of cycles this container can run until charges are depleted.

        If quantity of cycles can vary, mean value if taken (t2 laser ammo).
        Cycles, when quantity of charges consumed per cycle is more than left in
        container, are ignored (possible with ancillary armor repairers). None
        is returned if container can cycle without ammo consumption.
        """
        # Various item types consume charges during cycle, detect them based on
        # presence of charge_rate attribute in item type (modified attribute
        # value is always possible to fetch, as it has base value, so it's not
        # reliable way to detect it)
        if AttributeId.charge_rate in self._type_attributes:
            return self.__get_ammo_cycles()
        # Detect crystal-based item types using effects
        if self._type_default_effect_id in (
            EffectId.target_attack,
            EffectId.mining_laser
        ):
            return self.__get_crystal_mean_cycles()
        return None

    def __get_ammo_cycles(self):
        charge_rate = self.attributes.get(AttributeId.charge_rate)
        if not charge_rate or self.charge_quantity is None:
            return None
        cycles = self.charge_quantity // int(charge_rate)
        return cycles

    def __get_crystal_mean_cycles(self):
        charge_attribs = self.charge.attributes
        damageable = charge_attribs.get(AttributeId.crystals_get_damaged)
        hp = charge_attribs.get(AttributeId.hp)
        chance = charge_attribs.get(AttributeId.crystal_volatility_chance)
        damage = charge_attribs.get(AttributeId.crystal_volatility_damage)
        if (
            not damageable or
            hp is None or
            chance is None or
            damage is None or
            self.charge_quantity is None
        ):
            return None
        cycles = _float_to_int(hp / damage / chance) * self.charge_quantity
        return cycles

    @volatile_property
    def reload_time(self):
        """Returns item reload time in seconds."""
        # Return hardcoded 1.0 if item type has target_attack effect (various
        # lasers), else fetch reload time attribute from item
        if self._type_default_effect_id in (
            EffectId.target_attack,
            EffectId.mining_laser
        ):
            return 1.0
        reload_ms = self.attributes.get(AttributeId.reload_time)
        if reload_ms is None:
            return None
        return reload_ms / 1000

    # Properties used by attribute calculator
    @property
    def _other(self):
        return self.charge
