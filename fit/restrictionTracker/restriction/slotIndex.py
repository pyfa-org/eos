#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2012 Anton Vorobyov
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
#===============================================================================


from collections import namedtuple

from eos.const import Restriction
from eos.eve.const import Attribute
from eos.fit.restrictionTracker.exception import RegisterValidationError
from eos.fit.restrictionTracker.register import RestrictionRegister
from eos.util.keyedSet import KeyedSet


SlotIndexErrorData = namedtuple("SlotIndexErrorData", ("holderSlotIndex", "slotIndexHolders"))


class SlotIndexRegister(RestrictionRegister):
    """
    Class which implements common functionality for all
    registers, which track indices of occupied slots and
    disallow multiple holders reside within slot with the
    same index.
    """

    def __init__(self, slotIndexAttr, restrictionType):
        # This attribute's value on holder
        # represents their index of slot
        self.__slotIndexAttr = slotIndexAttr
        self.__restrictionType = restrictionType
        # All holders which possess index of slot
        # are stored in this container
        # Format: {slot index: {holders}}
        self.__slottedHolders = KeyedSet()

    def registerHolder(self, holder):
        # Skip items which don't have index specifier
        # or items with its value equal to None
        slotIndex = holder.item.attributes.get(self.__slotIndexAttr)
        if slotIndex is None:
            return
        self.__slottedHolders.addData(slotIndex, {holder})

    def unregisterHolder(self, holder):
        slotIndex = holder.item.attributes.get(self.__slotIndexAttr)
        if slotIndex is None:
            return
        self.__slottedHolders.rmData(slotIndex, {holder})

    def validate(self):
        taintedHolders = {}
        for slotIndex in self.__slottedHolders:
            slotIndexHolders = self.__slottedHolders[slotIndex]
            # If more than one item occupies the same slot, all
            # holders in this slot are tainted
            if len(slotIndexHolders) > 1:
                slotIndexHolders = frozenset(slotIndexHolders)
                for holder in slotIndexHolders:
                    taintedHolders[holder] = SlotIndexErrorData(holderSlotIndex=slotIndex,
                                                                slotIndexHolders=slotIndexHolders)
        if len(taintedHolders) > 0:
            raise RegisterValidationError(taintedHolders)

    @property
    def restrictionType(self):
        return self.__restrictionType


class SubsystemIndexRegister(SlotIndexRegister):
    """
    Implements restriction:
    Multiple subsystems can't be added into the same subsystem slot.

    Details:
    Slot to fill is determined by original item attributes.
    """

    def __init__(self):
        SlotIndexRegister.__init__(self, Attribute.subSystemSlot, Restriction.subsystemIndex)


class ImplantIndexRegister(SlotIndexRegister):
    """
    Implements restriction:
    Multiple implants can't be added into the same implant slot.

    Details:
    Slot to fill is determined by original item attributes.
    """

    def __init__(self):
        SlotIndexRegister.__init__(self, Attribute.implantness, Restriction.implantIndex)


class BoosterIndexRegister(SlotIndexRegister):
    """
    Implements restriction:
    Multiple boosters can't be added into the same booster slot.

    Details:
    Slot to fill is determined by original item attributes.
    """

    def __init__(self):
        SlotIndexRegister.__init__(self, Attribute.boosterness, Restriction.boosterIndex)
