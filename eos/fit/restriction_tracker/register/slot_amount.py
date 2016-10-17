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

from eos.const.eos import Restriction, Slot
from eos.fit.holder.item import Drone
from eos.fit.restriction_tracker.exception import RegisterValidationError
from .abc import RestrictionRegister


SlotAmountErrorData = namedtuple('SlotAmountErrorData', ('slots_used', 'slots_max_allowed'))


class SlotAmountRegister(RestrictionRegister):
    """
    Class which implements common functionality for all
    registers, which track amount of occupied ship slots
    against number of available ship slots.
    """

    def __init__(self, fit, stat_name, restriction_type):
        self.__restrictionType = restriction_type
        self._fit = fit
        # Use this stat name to get numbers from stats tracker
        self.__stat_name = stat_name
        self._slot_consumers = set()

    def register_holder(self, holder):
        self._slot_consumers.add(holder)

    def unregister_holder(self, holder):
        self._slot_consumers.discard(holder)

    def validate(self):
        # Use stats module to get max and used amount of slots
        stats = getattr(self._fit.stats, self.__stat_name)
        slots_used = stats.used
        # Can be None, so fall back to 0 in this case
        slots_max = stats.total or 0
        # If number of holders which take this slot is bigger
        # than number of available slots, then at least some
        # holders in container are tainted
        if slots_used > slots_max:
            tainted_holders = {}
            for holder in self._get_tainted_holders(slots_max):
                tainted_holders[holder] = SlotAmountErrorData(
                    slots_used=slots_used,
                    slots_max_allowed=slots_max
                )
            raise RegisterValidationError(tainted_holders)

    @property
    def restriction_type(self):
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
        SlotAmountRegister.__init__(self, fit, 'high_slots', Restriction.high_slot)

    def register_holder(self, holder):
        if holder in self._fit.modules.high:
            SlotAmountRegister.register_holder(self, holder)

    def _get_tainted_holders(self, slots_max):
        return self._fit.modules.high[slots_max:]


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
        SlotAmountRegister.__init__(self, fit, 'med_slots', Restriction.medium_slot)

    def register_holder(self, holder):
        if holder in self._fit.modules.med:
            SlotAmountRegister.register_holder(self, holder)

    def _get_tainted_holders(self, slots_max):
        return self._fit.modules.med[slots_max:]


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
        SlotAmountRegister.__init__(self, fit, 'low_slots', Restriction.low_slot)

    def register_holder(self, holder):
        if holder in self._fit.modules.low:
            SlotAmountRegister.register_holder(self, holder)

    def _get_tainted_holders(self, slots_max):
        return self._fit.modules.low[slots_max:]


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
        SlotAmountRegister.__init__(self, fit, 'rig_slots', Restriction.rig_slot)

    def register_holder(self, holder):
        if holder in self._fit.rigs:
            SlotAmountRegister.register_holder(self, holder)

    def _get_tainted_holders(self, slots_max):
        return self._slot_consumers


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
        SlotAmountRegister.__init__(self, fit, 'subsystem_slots', Restriction.subsystem_slot)

    def register_holder(self, holder):
        if holder in self._fit.subsystems:
            SlotAmountRegister.register_holder(self, holder)

    def _get_tainted_holders(self, slots_max):
        return self._slot_consumers


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
        SlotAmountRegister.__init__(self, fit, 'turret_slots', Restriction.turret_slot)

    def register_holder(self, holder):
        if Slot.turret in holder.item.slots:
            SlotAmountRegister.register_holder(self, holder)

    def _get_tainted_holders(self, slots_max):
        return self._slot_consumers


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
        SlotAmountRegister.__init__(self, fit, 'launcher_slots', Restriction.launcher_slot)

    def register_holder(self, holder):
        if Slot.launcher in holder.item.slots:
            SlotAmountRegister.register_holder(self, holder)

    def _get_tainted_holders(self, slots_max):
        return self._slot_consumers


class LaunchedDroneRegister(SlotAmountRegister):
    """
    Implements restriction:
    Number of launched drones should not exceed number of
    drones you're allowed to launch.

    Details:
    Only holders of Drone class are tracked.
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        SlotAmountRegister.__init__(self, fit, 'launched_drones', Restriction.launched_drone)

    def register_holder(self, holder):
        if isinstance(holder, Drone):
            SlotAmountRegister.register_holder(self, holder)

    def _get_tainted_holders(self, slots_max):
        return self._slot_consumers
