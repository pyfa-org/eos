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


from abc import ABCMeta, abstractmethod
from collections import namedtuple

from eos.const.eos import Restriction, State
from eos.const.eve import Effect
from eos.fit.item import Drone
from eos.fit.pubsub.message import (
    InstrStatesActivate, InstrStatesDeactivate, InstrEffectsActivate, InstrEffectsDeactivate
)
from .base import BaseRestrictionRegister
from ..exception import RestrictionValidationError


SlotAmountErrorData = namedtuple('SlotAmountErrorData', ('slots_used', 'slots_max_allowed'))


class SlotAmountRestrictionOrdered(BaseRestrictionRegister, metaclass=ABCMeta):
    """Base class for all slot amount restrictions"""

    def __init__(self, fit, stat_name, restriction_type):
        self.__restriction_type = restriction_type
        self._fit = fit
        # Use this stat name to get numbers from stats service
        self.__stat_name = stat_name

    def validate(self):
        # Use stats module to get max and used amount of slots
        stats = getattr(self._fit.stats, self.__stat_name)
        slots_used = stats.used
        # Can be None, so fall back to 0 in this case
        slots_max = stats.total or 0
        # If number of items which take this slot is bigger
        # than number of available slots, then at least some
        # items in container are tainted
        if slots_used > slots_max:
            tainted_items = {}
            for item in self._get_tainted_items(slots_max):
                tainted_items[item] = SlotAmountErrorData(
                    slots_used=slots_used,
                    slots_max_allowed=slots_max
                )
            raise RestrictionValidationError(tainted_items)

    @abstractmethod
    def _get_tainted_items(self, slots_max):
        ...

    @property
    def type(self):
        return self.__restriction_type


class SlotAmountRestrictionUnordered(SlotAmountRestrictionOrdered):
    """Base class for all slot amount restriction registers"""

    def __init__(self, fit, stat_name, restriction_type):
        SlotAmountRestrictionOrdered.__init__(self, fit, stat_name, restriction_type)
        self.__slot_consumers = set()

    def _register_item(self, item):
        self.__slot_consumers.add(item)

    def _unregister_item(self, item):
        self.__slot_consumers.discard(item)

    def _get_tainted_items(self, _):
        return self.__slot_consumers


class HighSlotRestriction(SlotAmountRestrictionOrdered):
    """
    Implements restriction:
    Number of high-slot items should not exceed number of
    high slots ship provides.

    Details:
    Only items placed to fit.modules.high are restricted.
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        SlotAmountRestrictionOrdered.__init__(self, fit, 'high_slots', Restriction.high_slot)
        fit._subscribe(self, self._handler_map.keys())

    def _get_tainted_items(self, slots_max):
        return self._fit.modules.high[slots_max:]

    _handler_map = {}


class MediumSlotRestriction(SlotAmountRestrictionOrdered):
    """
    Implements restriction:
    Number of medium-slot items should not exceed number of
    medium slots ship provides.

    Details:
    Only items placed to fit.modules.med are restricted.
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        SlotAmountRestrictionOrdered.__init__(self, fit, 'med_slots', Restriction.medium_slot)
        fit._subscribe(self, self._handler_map.keys())

    def _get_tainted_items(self, slots_max):
        return self._fit.modules.med[slots_max:]

    _handler_map = {}


class LowSlotRestriction(SlotAmountRestrictionOrdered):
    """
    Implements restriction:
    Number of low-slot items should not exceed number of
    low slots ship provides.

    Details:
    Only items placed to fit.modules.low are restricted.
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        SlotAmountRestrictionOrdered.__init__(self, fit, 'low_slots', Restriction.low_slot)
        fit._subscribe(self, self._handler_map.keys())

    def _get_tainted_items(self, slots_max):
        return self._fit.modules.low[slots_max:]

    _handler_map = {}


class RigSlotRestriction(SlotAmountRestrictionUnordered):
    """
    Implements restriction:
    Number of rig-slot items should not exceed number of
    rig slots ship provides.

    Details:
    Only items placed to fit.rigs are restricted.
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        SlotAmountRestrictionUnordered.__init__(self, fit, 'rig_slots', Restriction.rig_slot)
        fit._subscribe(self, self._handler_map.keys())

    def _handle_item_effects_activation(self, message):
        if Effect.rig_slot in message.effects:
            self._register_item(message.item)

    def _handle_item_effects_deactivation(self, message):
        if Effect.rig_slot in message.effects:
            self._unregister_item(message.item)

    _handler_map = {
        InstrEffectsActivate: _handle_item_effects_activation,
        InstrEffectsDeactivate: _handle_item_effects_deactivation
    }


class SubsystemSlotRestriction(SlotAmountRestrictionUnordered):
    """
    Implements restriction:
    Number of subsystem-slot items should not exceed number of
    subsystem slots ship provides.

    Details:
    Only items placed to fit.subsystems are restricted.
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        SlotAmountRestrictionUnordered.__init__(self, fit, 'subsystem_slots', Restriction.subsystem_slot)
        fit._subscribe(self, self._handler_map.keys())

    def _handle_item_effects_activation(self, message):
        if Effect.subsystem in message.effects:
            self._register_item(message.item)

    def _handle_item_effects_deactivation(self, message):
        if Effect.subsystem in message.effects:
            self._unregister_item(message.item)

    _handler_map = {
        InstrEffectsActivate: _handle_item_effects_activation,
        InstrEffectsDeactivate: _handle_item_effects_deactivation
    }


class TurretSlotRestriction(SlotAmountRestrictionUnordered):
    """
    Implements restriction:
    Number of turret-slot items should not exceed number of
    turret slots ship provides.

    Details:
    Only items which take turret slot are restricted.
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        SlotAmountRestrictionUnordered.__init__(self, fit, 'turret_slots', Restriction.turret_slot)
        fit._subscribe(self, self._handler_map.keys())

    def _handle_item_effects_activation(self, message):
        if Effect.turret_fitted in message.effects:
            self._register_item(message.item)

    def _handle_item_effects_deactivation(self, message):
        if Effect.turret_fitted in message.effects:
            self._unregister_item(message.item)

    _handler_map = {
        InstrEffectsActivate: _handle_item_effects_activation,
        InstrEffectsDeactivate: _handle_item_effects_deactivation
    }


class LauncherSlotRestriction(SlotAmountRestrictionUnordered):
    """
    Implements restriction:
    Number of launcher-slot items should not exceed number of
    launcher slots ship provides.

    Details:
    Only items which take launcher slot are restricted.
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        SlotAmountRestrictionUnordered.__init__(self, fit, 'launcher_slots', Restriction.launcher_slot)
        fit._subscribe(self, self._handler_map.keys())

    def _handle_item_effects_activation(self, message):
        if Effect.launcher_fitted in message.effects:
            self._register_item(message.item)

    def _handle_item_effects_deactivation(self, message):
        if Effect.launcher_fitted in message.effects:
            self._unregister_item(message.item)

    _handler_map = {
        InstrEffectsActivate: _handle_item_effects_activation,
        InstrEffectsDeactivate: _handle_item_effects_deactivation
    }


class LaunchedDroneRestriction(SlotAmountRestrictionUnordered):
    """
    Implements restriction:
    Number of launched drones should not exceed number of
    drones you're allowed to launch.

    Details:
    Only items of Drone class are restricted.
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        SlotAmountRestrictionUnordered.__init__(self, fit, 'launched_drones', Restriction.launched_drone)
        fit._subscribe(self, self._handler_map.keys())

    def _handle_item_states_activation(self, message):
        if isinstance(message.item, Drone) and State.online in message.states:
            self._register_item(message.item)

    def _handle_item_states_deactivation(self, message):
        if isinstance(message.item, Drone) and State.online in message.states:
            self._unregister_item(message.item)

    _handler_map = {
        InstrStatesActivate: _handle_item_states_activation,
        InstrStatesDeactivate: _handle_item_states_deactivation
    }
