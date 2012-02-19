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
from eos.fit.restrictionTracker.exception import HighSlotException, MediumSlotException, LowSlotException, \
RigSlotException, SubsystemSlotException, TurretSlotException, LauncherSlotException
from eos.fit.restrictionTracker.register import RestrictionRegister


class SlotNumberRegister(RestrictionRegister):
    """
    Class which implements common functionality for all
    registers, which track number of occupied ship slots
    against number of available ship slots.
    """

    def __init__(self, fit, slotType, slotAmountAttr, exceptionClass):
        self._fit = fit
        # Keeps slot type we're tracking
        self.__slotType = slotType
        # Modified ship holder attribute with this ID
        # contains number of available slots as value
        self.__slotAmountAttr = slotAmountAttr
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
        shipHolder = self._fit.ship
        try:
            shipHolderAttribs = shipHolder.attributes
        except AttributeError:
            providedSlots = 0
        else:
            try:
                providedSlots = shipHolderAttribs[self.__slotAmountAttr]
            except KeyError:
                providedSlots = 0
        # Assuming each holder takes exactly one slot, check
        # if we have enough of them; if number of holders which
        # take this slot is bigger than number of available slots,
        # then all holders in container are tainted
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
    For validation, modified amount of high slots is taken
    from ship holder.
    """

    def __init__(self, fit):
        SlotNumberRegister.__init__(self, fit, Slot.moduleHigh, Attribute.hiSlots, HighSlotException)


class MediumSlotRegister(SlotNumberRegister):
    """
    Implements restriction:
    Number of medium-slot holders should not exceed number of
    medium slots ship provides.

    Details:
    Only holders belonging to ship are tracked.
    For validation, modified amount of medium slots is taken
    from ship holder.
    """

    def __init__(self, fit):
        SlotNumberRegister.__init__(self, fit, Slot.moduleMed, Attribute.medSlots, MediumSlotException)


class LowSlotRegister(SlotNumberRegister):
    """
    Implements restriction:
    Number of low-slot holders should not exceed number of
    low slots ship provides.

    Details:
    Only holders belonging to ship are tracked.
    For validation, modified amount of low slots is taken
    from ship holder.
    """

    def __init__(self, fit):
        SlotNumberRegister.__init__(self, fit, Slot.moduleLow, Attribute.lowSlots, LowSlotException)


class RigSlotRegister(SlotNumberRegister):
    """
    Implements restriction:
    Number of rig-slot holders should not exceed number of
    rig slots ship provides.

    Details:
    Only holders belonging to ship are tracked.
    For validation, modified amount of rig slots is taken
    from ship holder.
    """

    def __init__(self, fit):
        SlotNumberRegister.__init__(self, fit, Slot.rig, Attribute.rigSlots, RigSlotException)


class SubsystemSlotRegister(SlotNumberRegister):
    """
    Implements restriction:
    Number of subsystem-slot holders should not exceed number of
    subsystem slots ship provides.

    Details:
    Only holders belonging to ship are tracked.
    For validation, modified amount of subsystem slots is taken
    from ship holder.
    """

    def __init__(self, fit):
        SlotNumberRegister.__init__(self, fit, Slot.subsystem, Attribute.maxSubSystems, SubsystemSlotException)


class TurretSlotRegister(SlotNumberRegister):
    """
    Implements restriction:
    Number of turret-slot holders should not exceed number of
    turret slots ship provides.

    Details:
    Only holders belonging to ship are tracked.
    For validation, modified amount of turret slots is taken
    from ship holder.
    """

    def __init__(self, fit):
        SlotNumberRegister.__init__(self, fit, Slot.turret, Attribute.turretSlotsLeft, TurretSlotException)


class LauncherSlotRegister(SlotNumberRegister):
    """
    Implements restriction:
    Number of launcher-slot holders should not exceed number of
    launcher slots ship provides.

    Details:
    Only holders belonging to ship are tracked.
    For validation, modified amount of launcher slots is taken
    from ship holder.
    """

    def __init__(self, fit):
        SlotNumberRegister.__init__(self, fit, Slot.launcher, Attribute.launcherSlotsLeft, LauncherSlotException)
