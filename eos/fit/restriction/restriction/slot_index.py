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


from abc import ABCMeta
from abc import abstractmethod
from collections import namedtuple

from eos.const.eos import Restriction
from eos.const.eve import AttrId
from eos.fit.message import ItemLoaded
from eos.fit.message import ItemUnloaded
from eos.util.keyed_storage import KeyedStorage
from .base import BaseRestrictionRegister
from ..exception import RestrictionValidationError


SlotIndexErrorData = namedtuple('SlotIndexErrorData', ('slot_index',))


class SlotIndexRestrictionRegister(BaseRestrictionRegister, metaclass=ABCMeta):
    """Base class for all slot index restrictions.

    It doesn't allow multiple items to take the same numbered slot.
    """

    def __init__(self, fit):
        # All items which possess index of slot are stored in this container
        # Format: {slot index: {items}}
        self.__index_item_map = KeyedStorage()
        fit._subscribe(self, self._handler_map.keys())

    @property
    @abstractmethod
    def _slot_index_attr_id(self):
        """This attribute's value on item represents index of slot."""
        ...

    def _handle_item_loaded(self, msg):
        # Skip items which don't have index specified
        slot_index = msg.item._type_attrs.get(self._slot_index_attr_id)
        if slot_index is None:
            return
        self.__index_item_map.add_data_entry(slot_index, msg.item)

    def _handle_item_unloaded(self, msg):
        slot_index = msg.item._type_attrs.get(self._slot_index_attr_id)
        if slot_index is None:
            return
        self.__index_item_map.rm_data_entry(slot_index, msg.item)

    _handler_map = {
        ItemLoaded: _handle_item_loaded,
        ItemUnloaded: _handle_item_unloaded}

    def validate(self):
        tainted_items = {}
        for slot_index, slot_index_items in self.__index_item_map.items():
            # If more than one item occupies the same slot, all items in this
            # slot are tainted
            if len(slot_index_items) > 1:
                for item in slot_index_items:
                    tainted_items[item] = SlotIndexErrorData(
                        slot_index=slot_index)
        if tainted_items:
            raise RestrictionValidationError(tainted_items)


class SubsystemIndexRestrictionRegister(SlotIndexRestrictionRegister):
    """Multiple subsystems can't be added into the same subsystem slot.

    Details:
        Slot to occupy is determined by item type attributes.
    """

    _slot_index_attr_id = AttrId.subsystem_slot

    @property
    def type(self):
        return Restriction.subsystem_index


class ImplantIndexRestrictionRegister(SlotIndexRestrictionRegister):
    """Multiple implants can't be added into the same implant slot.

    Details:
        Slot to occupy is determined by item type attributes.
    """

    _slot_index_attr_id = AttrId.implantness

    @property
    def type(self):
        return Restriction.implant_index


class BoosterIndexRestrictionRegister(SlotIndexRestrictionRegister):
    """Multiple boosters can't be added into the same booster slot.

    Details:
        Slot to occupy is determined by item type attributes.
    """

    _slot_index_attr_id = AttrId.boosterness

    @property
    def type(self):
        return Restriction.booster_index
