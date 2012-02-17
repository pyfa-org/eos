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


from eos.const import Location
from eos.const import Slot
from eos.eve.const import Attribute
from eos.fit.attributeCalculator.exception import NoAttributeException
from eos.fit.restrictionTracker.exception import HighSlotException
from eos.fit.restrictionTracker.registerAbc import RestrictionRegister


class SlotNumberRegister(RestrictionRegister):
    """
    Class which implements common functionality for all
    registers, which track number of occupied slots vs
    number of available slots.
    """

    def __init__(self, fit, slotType, slotAmountAttr, exceptionClass):
        self.__fit = fit
        # Keeps slot type we're tracking
        self.__slotType = slotType
        # Modified ship holder attribute with this ID
        # contains number of available slots as value
        self.__slotAmountAttr = slotAmountAttr
        # Exception class to throw on validation failure
        self.__exceptionClass = exceptionClass
        # Container for holders which occupy slot
        # being tracked by register
        # Format: {holders}
        self.__slotConsumers = set()

    def registerHolder(self, holder):
        # Ignore holders which do not belong to ship
        if holder._location != Location.ship:
            return
        # Ignore all holders which do not occupy slot type
        # we're dealing with
        if (self.__slotType in holder.item.slots) is not True:
            return
        self.__slotConsumers.add(holder)

    def unregisterHolder(self, holder):
        self.__slotConsumers.discard(holder)

    def validate(self):
        # Get number of tracked slots ship provides,
        # if fit doesn't have ship or ship doesn't
        # have corresponding slot attribute, assume number
        # of provided slots is 0
        shipHolder = self.__fit.ship
        try:
            shipHolderAttribs = shipHolder.attributes
        except AttributeError:
            providedSlots = 0
        else:
            try:
                providedSlots = shipHolderAttribs[self.__slotAmountAttr]
            except NoAttributeException:
                providedSlots = 0
        # Assuming each holder takes exactly one slot, check
        # if we have enough of them; if number of  slot users
        # is bigger than number of available slots, then all
        # holders in container are tainted
        if len(self.__slotConsumers) > providedSlots:
            taintedHolders = set()
            taintedHolders.update(self.__slotConsumers)
            raise self.__exceptionClass(taintedHolders)


class HighSlotRegister(SlotNumberRegister):
    """
    Implements restriction:
    Number of high-slot holders should not exceed number of
    high slots ship provides.

    Details:
    Only holders belonging to ship are tracked.
    For validation, modified amount of high slots is taken.
    """

    def __init__(self, fit):
        SlotNumberRegister.__init__(self, fit, Slot.moduleHigh, Attribute.hiSlots, HighSlotException)
