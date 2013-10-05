#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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

from eos.const.eos import Restriction, Slot
from eos.fit.restrictionTracker.exception import RegisterValidationError
from .abc import RestrictionRegister


SlotAmountErrorData = namedtuple('SlotAmountErrorData', ('slotsUsed', 'slotsMaxAllowed'))


class SlotAmountRegister(RestrictionRegister):
    """
    Class which implements common functionality for all
    registers, which track amount of occupied ship slots
    against number of available ship slots.
    """

    def __init__(self, fit, statName, restrictionType):
        self.__restrictionType = restrictionType
        self._fit = fit
        # Use this stat name to get numbers from stats tracker
        self.__statName = statName
        self._slotConsumers = set()

    def registerHolder(self, holder):
        self._slotConsumers.add(holder)

    def unregisterHolder(self, holder):
        self._slotConsumers.discard(holder)

    def validate(self):
        # Use stats module to get max and used amount of slots
        stats = getattr(self._fit.stats, self.__statName)
        slotsUsed = stats.used
        # Can be None, so fall back to 0 in this case
        slotsMax = stats.total or 0
        # If number of holders which take this slot is bigger
        # than number of available slots, then at least some
        # holders in container are tainted
        if slotsUsed > slotsMax:
            taintedHolders = {}
            for holder in self._getTaintedHolders(slotsMax):
                # If subclasses specify their own filter, use it to skip valid holders
                if hasattr(self, '_taintFilter') and not self._taintFilter(holder):
                    continue
                taintedHolders[holder] = SlotAmountErrorData(slotsUsed=slotsUsed,
                                                             slotsMaxAllowed=slotsMax)
            raise RegisterValidationError(taintedHolders)

    @property
    def restrictionType(self):
        return self.__restrictionType


class HighSlotRegister(SlotAmountRegister):
    """
    Implements restriction:
    Number of high-slot holders should not exceed number of
    high slots ship provides.

    Details:
    Only holders placed to fit.modules.high are tracked.
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        SlotAmountRegister.__init__(self, fit, 'highSlots', Restriction.highSlot)

    def registerHolder(self, holder):
        if holder in self._fit.modules.high:
            SlotAmountRegister.registerHolder(self, holder)

    def _getTaintedHolders(self, slotsMax):
        return self._fit.modules.high[slotsMax:]


class MediumSlotRegister(SlotAmountRegister):
    """
    Implements restriction:
    Number of medium-slot holders should not exceed number of
    medium slots ship provides.

    Details:
    Only holders placed to fit.modules.med are tracked.
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        SlotAmountRegister.__init__(self, fit, 'medSlots', Restriction.mediumSlot)

    def registerHolder(self, holder):
        if holder in self._fit.modules.med:
            SlotAmountRegister.registerHolder(self, holder)

    def _getTaintedHolders(self, slotsMax):
        return self._fit.modules.med[slotsMax:]


class LowSlotRegister(SlotAmountRegister):
    """
    Implements restriction:
    Number of low-slot holders should not exceed number of
    low slots ship provides.

    Details:
    Only holders placed to fit.modules.low are tracked.
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        SlotAmountRegister.__init__(self, fit, 'lowSlots', Restriction.lowSlot)

    def registerHolder(self, holder):
        if holder in self._fit.modules.low:
            SlotAmountRegister.registerHolder(self, holder)

    def _getTaintedHolders(self, slotsMax):
        return self._fit.modules.low[slotsMax:]


class RigSlotRegister(SlotAmountRegister):
    """
    Implements restriction:
    Number of rig-slot holders should not exceed number of
    rig slots ship provides.

    Details:
    Only holders placed to fit.rigs are tracked.
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        SlotAmountRegister.__init__(self, fit, 'rigSlots', Restriction.rigSlot)

    def registerHolder(self, holder):
        if holder in self._fit.rigs:
            SlotAmountRegister.registerHolder(self, holder)

    def _getTaintedHolders(self, slotsMax):
        return self._slotConsumers


class SubsystemSlotRegister(SlotAmountRegister):
    """
    Implements restriction:
    Number of subsystem-slot holders should not exceed number of
    subsystem slots ship provides.

    Details:
    Only holders placed to fit.subsystems are tracked.
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        SlotAmountRegister.__init__(self, fit, 'subsystemSlots', Restriction.subsystemSlot)

    def registerHolder(self, holder):
        if holder in self._fit.subsystems:
            SlotAmountRegister.registerHolder(self, holder)

    def _getTaintedHolders(self, slotsMax):
        return self._slotConsumers


class TurretSlotRegister(SlotAmountRegister):
    """
    Implements restriction:
    Number of turret-slot holders should not exceed number of
    turret slots ship provides.

    Details:
    Only holders which take turret slot are tracked.
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        SlotAmountRegister.__init__(self, fit, 'turretSlots', Restriction.turretSlot)

    def registerHolder(self, holder):
        if Slot.turret in holder.item.slots:
            SlotAmountRegister.registerHolder(self, holder)

    def _getTaintedHolders(self, slotsMax):
        return self._slotConsumers


class LauncherSlotRegister(SlotAmountRegister):
    """
    Implements restriction:
    Number of launcher-slot holders should not exceed number of
    launcher slots ship provides.

    Details:
    Only holders which take launcher slot are tracked.
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        SlotAmountRegister.__init__(self, fit, 'launcherSlots', Restriction.launcherSlot)

    def registerHolder(self, holder):
        if Slot.launcher in holder.item.slots:
            SlotAmountRegister.registerHolder(self, holder)

    def _getTaintedHolders(self, slotsMax):
        return self._slotConsumers
