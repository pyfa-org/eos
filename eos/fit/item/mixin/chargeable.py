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
from eos.fit.item import Charge
from eos.fit.item_container import ItemDescriptor
from eos.util.float import float_to_int
from .base import BaseItemMixin


class ChargeableMixin(BaseItemMixin):
    """Supports ability to load charges into items.

    Args:
        charge: Charge to be loaded into item.

    Cooperative methods:
        __init__
        _get_child_items
    """

    def __init__(self, charge, **kwargs):
        super().__init__(**kwargs)
        self.charge = charge

    charge = ItemDescriptor('_charge', Charge)

    def _get_child_items(self):
        try:
            child_getter = super()._get_child_items
        except AttributeError:
            child_items = set()
        else:
            child_items = child_getter()
        if self.charge is not None:
            child_items.add(self.charge)
        return child_items

    @property
    def charge_quantity(self):
        """Max quantity of loadable charges.

        It depends on capacity of this item and volume of charge.

        Returns:
            Quantity of loadable charges as integer. If any of necessary
            attribute values is not defined, or no charge is found in item, None
            is returned.
        """
        if self.charge is None:
            return None
        container_capacity = self.attrs.get(AttrId.capacity)
        charge_volume = self.charge.attrs.get(AttrId.volume)
        if container_capacity is None or charge_volume is None:
            return None
        charges = float_to_int(container_capacity / charge_volume)
        return charges

    @property
    def cycles_until_reload(self):
        """Quantity of cycles item can run until charges are depleted."""
        item_type = self._type
        if item_type is None:
            return None
        try:
            getter = item_type.default_effect.get_cycles_until_reload
        except AttributeError:
            return 0
        else:
            return getter(self)

    @property
    def reload_time(self):
        """Returns item reload time in seconds."""
        time_ms = self.attrs.get(AttrId.reload_time)
        try:
            return time_ms / 1000
        except TypeError:
            return time_ms
