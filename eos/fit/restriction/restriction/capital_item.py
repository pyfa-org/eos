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


from collections import namedtuple

from eos.const.eos import Restriction
from eos.const.eve import Attribute
from eos.fit.item import Ship, ModuleHigh, ModuleMed, ModuleLow
from eos.fit.pubsub.message import InstrItemAdd, InstrItemRemove
from .base import BaseRestrictionRegister
from ..exception import RestrictionValidationError


# Items of volume bigger than this are considered as capital
MAX_SUBCAP_VOLUME = 3500
TRACKED_ITEM_CLASSES = (ModuleHigh, ModuleMed, ModuleLow)


CapitalItemErrorData = namedtuple('CapitalItemErrorData', ('item_volume', 'max_subcap_volume'))


class CapitalItemRestriction(BaseRestrictionRegister):
    """
    Implements restriction:
    To fit items with volume bigger than 4000, ship must
    have IsCapitalShip attribute set to 1.

    Details:
    Only modules are restricted.
    For validation, eve type volume value is taken. If volume
        attribute is absent, item is not restricted.
    """

    def __init__(self, fit):
        self.__current_ship = None
        self.__capital_items = set()
        fit._subscribe(self, self._handler_map.keys())

    def _handle_item_addition(self, message):
        if isinstance(message.item, Ship):
            self.__current_ship = message.item
        if not isinstance(message.item, TRACKED_ITEM_CLASSES):
            return
        # Ignore items with no volume attribute and items with
        # volume which satisfies us regardless of ship type
        try:
            item_volume = message.item._eve_type.attributes[Attribute.volume]
        except KeyError:
            return
        if item_volume <= MAX_SUBCAP_VOLUME:
            return
        self.__capital_items.add(message.item)

    def _handle_item_removal(self, message):
        if isinstance(message.item, Ship):
            self.__current_ship = None
        self.__capital_items.discard(message.item)

    _handler_map = {
        InstrItemAdd: _handle_item_addition,
        InstrItemRemove: _handle_item_removal
    }

    def validate(self):
        # Skip validation only if ship has special special attribute set to 1
        try:
            ship_eve_type = self.__current_ship._eve_type
        except AttributeError:
            pass
        else:
            if ship_eve_type.attributes.get(Attribute.is_capital_size):
                return
        # If we got here, then we're dealing with non-capital
        # ship, and all registered items are tainted
        if self.__capital_items:
            tainted_items = {}
            for item in self.__capital_items:
                item_volume = item._eve_type.attributes[Attribute.volume]
                tainted_items[item] = CapitalItemErrorData(
                    item_volume=item_volume,
                    max_subcap_volume=MAX_SUBCAP_VOLUME
                )
            raise RestrictionValidationError(tainted_items)

    @property
    def type(self):
        return Restriction.capital_item
