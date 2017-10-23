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
from eos.const.eve import Attribute
from eos.fit.pubsub.message import InstrItemAdd, InstrItemRemove
from eos.util.keyed_storage import KeyedStorage
from .base import BaseRestrictionRegister
from ..exception import RestrictionValidationError


SlotIndexErrorData = namedtuple('SlotIndexErrorData', ('item_slot_index',))


class SlotIndexRestrictionRegister(BaseRestrictionRegister):
    """Base class for all slot index restrictions.

    It doesn't allow multiple items to take the same numbered slot.
    """

    def __init__(self, msg_broker, slot_index_attr):
        # This attribute's value on item represents their index of slot
        self.__slot_index_attr = slot_index_attr
        # All items which possess index of slot are stored in this container
        # Format: {slot index: {items}}
        self.__slotted_items = KeyedStorage()
        msg_broker._subscribe(self, self._handler_map.keys())

    def _handle_item_addition(self, message):
        # Skip items which don't have index specified
        slot_index = message.item._eve_type_attributes.get(
            self.__slot_index_attr)
        if slot_index is None:
            return
        self.__slotted_items.add_data_entry(slot_index, message.item)

    def _handle_item_removal(self, message):
        slot_index = message.item._eve_type_attributes.get(
            self.__slot_index_attr)
        if slot_index is None:
            return
        self.__slotted_items.rm_data_entry(slot_index, message.item)

    _handler_map = {
        InstrItemAdd: _handle_item_addition,
        InstrItemRemove: _handle_item_removal}

    def validate(self):
        tainted_items = {}
        for slot_index in self.__slotted_items:
            slot_index_items = self.__slotted_items[slot_index]
            # If more than one item occupies the same slot, all items in this
            # slot are tainted
            if len(slot_index_items) > 1:
                for item in slot_index_items:
                    tainted_items[item] = SlotIndexErrorData(
                        item_slot_index=slot_index)
        if tainted_items:
            raise RestrictionValidationError(tainted_items)


class SubsystemIndexRestrictionRegister(SlotIndexRestrictionRegister):
    """Multiple subsystems can't be added into the same subsystem slot.

    Details:
        Slot to occupy is determined by eve type attributes.
    """

    def __init__(self, msg_broker):
        SlotIndexRestrictionRegister.__init__(
            self, msg_broker, Attribute.subsystem_slot)

    @property
    def type(self):
        return Restriction.subsystem_index


class ImplantIndexRestrictionRegister(SlotIndexRestrictionRegister):
    """Multiple implants can't be added into the same implant slot.

    Details:
        Slot to occupy is determined by eve type attributes.
    """

    def __init__(self, msg_broker):
        SlotIndexRestrictionRegister.__init__(
            self, msg_broker, Attribute.implantness)

    @property
    def type(self):
        return Restriction.implant_index


class BoosterIndexRestrictionRegister(SlotIndexRestrictionRegister):
    """Multiple boosters can't be added into the same booster slot.

    Details:
        Slot to occupy is determined by eve type attributes.
    """

    def __init__(self, msg_broker):
        SlotIndexRestrictionRegister.__init__(
            self, msg_broker, Attribute.boosterness)

    @property
    def type(self):
        return Restriction.booster_index
