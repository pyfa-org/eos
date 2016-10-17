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


from collections import namedtuple

from eos.const.eos import Restriction
from eos.const.eve import Attribute
from eos.fit.restriction_tracker.exception import RegisterValidationError
from eos.util.keyed_set import KeyedSet
from .abc import RestrictionRegister


SlotIndexErrorData = namedtuple('SlotIndexErrorData', ('holder_slot_index',))


class SlotIndexRegister(RestrictionRegister):
    """
    Class which implements common functionality for all
    registers, which track indices of occupied slots and
    disallow multiple holders reside within slot with the
    same index.
    """

    def __init__(self, slot_index_attr, restriction_type):
        # This attribute's value on holder
        # represents their index of slot
        self.__slot_index_attr = slot_index_attr
        self.__restriction_type = restriction_type
        # All holders which possess index of slot
        # are stored in this container
        # Format: {slot index: {holders}}
        self.__slotted_holders = KeyedSet()

    def register_holder(self, holder):
        # Skip items which don't have index specifier
        slot_index = holder.item.attributes.get(self.__slot_index_attr)
        if slot_index is None:
            return
        self.__slotted_holders.add_data(slot_index, holder)

    def unregister_holder(self, holder):
        slot_index = holder.item.attributes.get(self.__slot_index_attr)
        if slot_index is None:
            return
        self.__slotted_holders.rm_data(slot_index, holder)

    def validate(self):
        tainted_holders = {}
        for slot_index in self.__slotted_holders:
            slot_index_holders = self.__slotted_holders[slot_index]
            # If more than one item occupies the same slot, all
            # holders in this slot are tainted
            if len(slot_index_holders) > 1:
                for holder in slot_index_holders:
                    tainted_holders[holder] = SlotIndexErrorData(holder_slot_index=slot_index)
        if tainted_holders:
            raise RegisterValidationError(tainted_holders)

    @property
    def restriction_type(self):
        return self.__restriction_type


class SubsystemIndexRegister(SlotIndexRegister):
    """
    Implements restriction:
    Multiple subsystems can't be added into the same subsystem slot.

    Details:
    Slot to fill is determined by original item attributes.
    """

    def __init__(self):
        SlotIndexRegister.__init__(self, Attribute.subsystem_slot, Restriction.subsystem_index)


class ImplantIndexRegister(SlotIndexRegister):
    """
    Implements restriction:
    Multiple implants can't be added into the same implant slot.

    Details:
    Slot to fill is determined by original item attributes.
    """

    def __init__(self):
        SlotIndexRegister.__init__(self, Attribute.implantness, Restriction.implant_index)


class BoosterIndexRegister(SlotIndexRegister):
    """
    Implements restriction:
    Multiple boosters can't be added into the same booster slot.

    Details:
    Slot to fill is determined by original item attributes.
    """

    def __init__(self):
        SlotIndexRegister.__init__(self, Attribute.boosterness, Restriction.booster_index)
