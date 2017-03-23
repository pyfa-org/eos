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
from eos.util.keyed_set import KeyedSet
from .base import BaseRestriction
from ..exception import RestrictionValidationError


SlotIndexErrorData = namedtuple('SlotIndexErrorData', ('item_slot_index',))


class SlotIndexRestriction(BaseRestriction):
    """
    Class which implements common functionality for all
    registers, which track indices of occupied slots and
    disallow multiple items reside within slot with the
    same index.
    """

    def __init__(self, slot_index_attr, restriction_type):
        # This attribute's value on item
        # represents their index of slot
        self.__slot_index_attr = slot_index_attr
        self.__restriction_type = restriction_type
        # All items which possess index of slot
        # are stored in this container
        # Format: {slot index: {items}}
        self.__slotted_items = KeyedSet()

    def register_item(self, item):
        # Skip items which don't have index specified
        slot_index = item._eve_type.attributes.get(self.__slot_index_attr)
        if slot_index is None:
            return
        self.__slotted_items.add_data(slot_index, item)

    def unregister_item(self, item):
        slot_index = item._eve_type.attributes.get(self.__slot_index_attr)
        if slot_index is None:
            return
        self.__slotted_items.rm_data(slot_index, item)

    def validate(self):
        tainted_items = {}
        for slot_index in self.__slotted_items:
            slot_index_items = self.__slotted_items[slot_index]
            # If more than one item occupies the same slot, all
            # items in this slot are tainted
            if len(slot_index_items) > 1:
                for item in slot_index_items:
                    tainted_items[item] = SlotIndexErrorData(item_slot_index=slot_index)
        if tainted_items:
            raise RestrictionValidationError(tainted_items)

    @property
    def type(self):
        return self.__restriction_type


class SubsystemIndexRestriction(SlotIndexRestriction):
    """
    Implements restriction:
    Multiple subsystems can't be added into the same subsystem slot.

    Details:
    Slot to occupy is determined by eve type attributes.
    """

    def __init__(self):
        SlotIndexRestriction.__init__(self, Attribute.subsystem_slot, Restriction.subsystem_index)


class ImplantIndexRestriction(SlotIndexRestriction):
    """
    Implements restriction:
    Multiple implants can't be added into the same implant slot.

    Details:
    Slot to occupy is determined by eve type attributes.
    """

    def __init__(self):
        SlotIndexRestriction.__init__(self, Attribute.implantness, Restriction.implant_index)


class BoosterIndexRestriction(SlotIndexRestriction):
    """
    Implements restriction:
    Multiple boosters can't be added into the same booster slot.

    Details:
    Slot to occupy is determined by eve type attributes.
    """

    def __init__(self):
        SlotIndexRestriction.__init__(self, Attribute.boosterness, Restriction.booster_index)
