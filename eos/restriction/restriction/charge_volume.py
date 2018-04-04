# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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


from collections import namedtuple

from eos.const.eos import Restriction
from eos.const.eve import AttrId
from eos.message import ItemLoaded
from eos.message import ItemUnloaded
from eos.restriction.exception import RestrictionValidationError
from .base import BaseRestrictionRegister


ChargeVolumeErrorData = namedtuple(
    'ChargeVolumeErrorData', ('volume', 'max_allowed_volume'))


class ChargeVolumeRestrictionRegister(BaseRestrictionRegister):
    """Volume of charge loaded into container should not excess its capacity.

    Details:
        Charge volume and container capacity are taken from item type
            attributes.
        If not specified, volume and/or capacity are assumed to be 0.
    """

    type = Restriction.charge_volume

    def __init__(self, msg_broker):
        self.__containers = set()
        msg_broker._subscribe(self, self._handler_map.keys())

    def _handle_item_loaded(self, msg):
        # Ignore container items without charge attribute
        if not hasattr(msg.item, 'charge'):
            return
        self.__containers.add(msg.item)

    def _handle_item_unloaded(self, msg):
        self.__containers.discard(msg.item)

    _handler_map = {
        ItemLoaded: _handle_item_loaded,
        ItemUnloaded: _handle_item_unloaded}

    def validate(self):
        tainted_items = {}
        for container in self.__containers:
            charge = container.charge
            if charge is None:
                continue
            # Get volume and capacity with 0 as fallback, and compare them,
            # raising error when charge can't fit
            charge_volume = charge._type_attrs.get(AttrId.volume, 0)
            container_capacity = container._type_attrs.get(AttrId.capacity, 0)
            if charge_volume > container_capacity:
                tainted_items[charge] = ChargeVolumeErrorData(
                    volume=charge_volume,
                    max_allowed_volume=container_capacity)
        if tainted_items:
            raise RestrictionValidationError(tainted_items)
