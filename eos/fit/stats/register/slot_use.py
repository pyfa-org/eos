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

from eos.const.eos import State
from eos.const.eve import Effect
from eos.fit.item import Drone
from eos.fit.pubsub.message import (
    InstrStatesActivate, InstrStatesDeactivate, InstrEffectsActivate, InstrEffectsDeactivate
)
from .base import BaseStatRegister


class SlotUseRegister(BaseStatRegister, metaclass=ABCMeta):

    def __init__(self, fit):
        self._slot_users = set()
        fit._subscribe(self, self._handler_map.keys())

    def _register_item(self, item):
        self._slot_users.add(item)

    def _unregister_item(self, item):
        self._slot_users.discard(item)

    @property
    @abstractmethod
    def slots_used(self):
        ...


class SlotUseUnorderedRegister(SlotUseRegister):

    @property
    def slots_used(self):
        return len(self._slot_users)


class SlotUseOrderedRegister(SlotUseRegister):

    @property
    def slots_used(self):
        return max((i._container_position or 0 for i in self._slot_users), default=-1) + 1


class HighSlotUseRegister(SlotUseOrderedRegister):

    def _handle_item_effects_activation(self, message):
        if Effect.hi_power in message.effects:
            SlotUseRegister._register_item(self, message.item)

    def _handle_item_effects_deactivation(self, message):
        if Effect.hi_power in message.effects:
            SlotUseRegister._unregister_item(self, message.item)

    _handler_map = {
        InstrEffectsActivate: _handle_item_effects_activation,
        InstrEffectsDeactivate: _handle_item_effects_deactivation
    }


class MediumSlotUseRegister(SlotUseOrderedRegister):

    def _handle_item_effects_activation(self, message):
        if Effect.med_power in message.effects:
            SlotUseRegister._register_item(self, message.item)

    def _handle_item_effects_deactivation(self, message):
        if Effect.med_power in message.effects:
            SlotUseRegister._unregister_item(self, message.item)

    _handler_map = {
        InstrEffectsActivate: _handle_item_effects_activation,
        InstrEffectsDeactivate: _handle_item_effects_deactivation
    }


class LowSlotUseRegister(SlotUseOrderedRegister):

    def _handle_item_effects_activation(self, message):
        if Effect.lo_power in message.effects:
            SlotUseRegister._register_item(self, message.item)

    def _handle_item_effects_deactivation(self, message):
        if Effect.lo_power in message.effects:
            SlotUseRegister._unregister_item(self, message.item)

    _handler_map = {
        InstrEffectsActivate: _handle_item_effects_activation,
        InstrEffectsDeactivate: _handle_item_effects_deactivation
    }


class RigUseRegister(SlotUseUnorderedRegister):

    def _handle_item_effects_activation(self, message):
        if Effect.rig_slot in message.effects:
            SlotUseRegister._register_item(self, message.item)

    def _handle_item_effects_deactivation(self, message):
        if Effect.rig_slot in message.effects:
            SlotUseRegister._unregister_item(self, message.item)

    _handler_map = {
        InstrEffectsActivate: _handle_item_effects_activation,
        InstrEffectsDeactivate: _handle_item_effects_deactivation
    }


class SubsystemUseRegister(SlotUseUnorderedRegister):

    def _handle_item_effects_activation(self, message):
        if Effect.subsystem in message.effects:
            SlotUseRegister._register_item(self, message.item)

    def _handle_item_effects_deactivation(self, message):
        if Effect.subsystem in message.effects:
            SlotUseRegister._unregister_item(self, message.item)

    _handler_map = {
        InstrEffectsActivate: _handle_item_effects_activation,
        InstrEffectsDeactivate: _handle_item_effects_deactivation
    }


class TurretUseRegister(SlotUseUnorderedRegister):
    """
    Assist with calculation of amount of used turret slots.
    """

    def _handle_item_effects_activation(self, message):
        if Effect.turret_fitted in message.effects:
            SlotUseRegister._register_item(self, message.item)

    def _handle_item_effects_deactivation(self, message):
        if Effect.turret_fitted in message.effects:
            SlotUseRegister._unregister_item(self, message.item)

    _handler_map = {
        InstrEffectsActivate: _handle_item_effects_activation,
        InstrEffectsDeactivate: _handle_item_effects_deactivation
    }


class LauncherUseRegister(SlotUseUnorderedRegister):
    """
    Assist with calculation of amount of used launcher slots.
    """

    def _handle_item_effects_activation(self, message):
        if Effect.launcher_fitted in message.effects:
            SlotUseRegister._register_item(self, message.item)

    def _handle_item_effects_deactivation(self, message):
        if Effect.launcher_fitted in message.effects:
            SlotUseRegister._unregister_item(self, message.item)

    _handler_map = {
        InstrEffectsActivate: _handle_item_effects_activation,
        InstrEffectsDeactivate: _handle_item_effects_deactivation
    }


class LaunchedDroneRegister(SlotUseUnorderedRegister):
    """
    Assist with calculation of amount of launched drones.
    """

    def _handle_item_states_activation(self, message):
        if isinstance(message.item, Drone) and State.online in message.states:
            SlotUseRegister._register_item(self, message.item)

    def _handle_item_states_deactivation(self, message):
        if isinstance(message.item, Drone) and State.online in message.states:
            SlotUseRegister._unregister_item(self, message.item)

    _handler_map = {
        InstrStatesActivate: _handle_item_states_activation,
        InstrStatesDeactivate: _handle_item_states_deactivation
    }
