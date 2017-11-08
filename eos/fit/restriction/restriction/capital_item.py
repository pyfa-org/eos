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


from collections import namedtuple

from eos.const.eos import Restriction
from eos.const.eve import AttributeId
from eos.fit.item import ModuleHigh, ModuleLow, ModuleMed, Ship
from eos.fit.pubsub.message import ItemAdded, ItemRemoved
from .base import BaseRestrictionRegister
from ..exception import RestrictionValidationError


# Items of volume bigger than this are considered as capital
MAX_SUBCAP_VOLUME = 3500
TRACKED_ITEM_CLASSES = (ModuleHigh, ModuleMed, ModuleLow)


CapitalItemErrorData = namedtuple(
    'CapitalItemErrorData', ('item_volume', 'max_subcap_volume'))


class CapitalItemRestrictionRegister(BaseRestrictionRegister):
    """Do not let to fit capital modules to subcapitals.

    Details:
        Only modules with type volume greater than 3500 are restricted.
        Capital ships are ships whose type has non-zero isCapitalSize attribute
            value.
    """

    def __init__(self, msg_broker):
        self.__current_ship = None
        self.__capital_items = set()
        msg_broker._subscribe(self, self._handler_map.keys())

    def _handle_item_added(self, message):
        if isinstance(message.item, Ship):
            self.__current_ship = message.item
        if not isinstance(message.item, TRACKED_ITEM_CLASSES):
            return
        # Ignore items with no volume attribute and items with volume which
        # satisfies us regardless of ship type
        try:
            item_volume = message.item._type_attributes[AttributeId.volume]
        except KeyError:
            return
        if item_volume <= MAX_SUBCAP_VOLUME:
            return
        self.__capital_items.add(message.item)

    def _handle_item_removed(self, message):
        if message.item is self.__current_ship:
            self.__current_ship = None
        self.__capital_items.discard(message.item)

    _handler_map = {
        ItemAdded: _handle_item_added,
        ItemRemoved: _handle_item_removed}

    def validate(self):
        # Skip validation only if ship has special special attribute set value
        # which is evaluated as True
        ship = self.__current_ship
        if (
            ship is not None and
            ship._type_attributes.get(AttributeId.is_capital_size)
        ):
            return
        # If we got here, then we're dealing with non-capital ship, and all
        # registered items are tainted
        if self.__capital_items:
            tainted_items = {}
            for item in self.__capital_items:
                item_type_volume = item._type_attributes[AttributeId.volume]
                tainted_items[item] = CapitalItemErrorData(
                    item_volume=item_type_volume,
                    max_subcap_volume=MAX_SUBCAP_VOLUME)
            raise RestrictionValidationError(tainted_items)

    @property
    def type(self):
        return Restriction.capital_item
