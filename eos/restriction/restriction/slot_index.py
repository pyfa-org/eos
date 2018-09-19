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


from abc import ABCMeta
from abc import abstractmethod
from collections import namedtuple

from eos.const.eos import Restriction
from eos.const.eve import AttrId
from eos.item import Booster
from eos.item import Implant
from eos.item import Subsystem
from eos.pubsub.message import ItemLoaded
from eos.pubsub.message import ItemUnloaded
from eos.restriction.exception import RestrictionValidationError
from eos.util.keyed_storage import KeyedStorage
from .base import BaseRestrictionRegister


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

    @property
    @abstractmethod
    def _item_class(self):
        """Items belonging to this class are restricted."""
        ...

    def _handle_item_loaded(self, msg):
        item = msg.item
        # Skip items which do not belong to specified class. Initially there was
        # no such check, but there was issue with Amarr Battlecruisers skill. As
        # of 2018-09-19, it still has subSystemSlot attribute with value 125,
        # which overlaps with t3c core subsystems
        if not isinstance(item, self._item_class):
            return
        # Skip items which don't have index specified
        slot_index = item._type_attrs.get(self._slot_index_attr_id)
        if slot_index is None:
            return
        self.__index_item_map.add_data_entry(slot_index, item)

    def _handle_item_unloaded(self, msg):
        item = msg.item
        if not isinstance(item, self._item_class):
            return
        slot_index = item._type_attrs.get(self._slot_index_attr_id)
        if slot_index is None:
            return
        self.__index_item_map.rm_data_entry(slot_index, item)

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
        Only items of Subsystem class are restricted.
        Slot to occupy is determined by item type attributes.
    """

    type = Restriction.subsystem_index
    _item_class = Subsystem
    _slot_index_attr_id = AttrId.subsystem_slot


class ImplantIndexRestrictionRegister(SlotIndexRestrictionRegister):
    """Multiple implants can't be added into the same implant slot.

    Details:
        Only items of Implant class are restricted.
        Slot to occupy is determined by item type attributes.
    """

    type = Restriction.implant_index
    _item_class = Implant
    _slot_index_attr_id = AttrId.implantness


class BoosterIndexRestrictionRegister(SlotIndexRestrictionRegister):
    """Multiple boosters can't be added into the same booster slot.

    Details:
        Only items of Implant class are restricted.
        Slot to occupy is determined by item type attributes.
    """

    type = Restriction.booster_index
    _item_class = Booster
    _slot_index_attr_id = AttrId.boosterness
