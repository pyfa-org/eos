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


from eos.const.eos import State
from eos.const.eve import Attribute, Effect
from eos.fit.item import Drone
from eos.fit.pubsub.message import (
    InstrItemAdd, InstrItemRemove, InstrStatesActivate, InstrStatesDeactivate,
    InstrEffectsActivate, InstrEffectsDeactivate
)
from .base import BaseStatRegister


class ResourceUseRegister(BaseStatRegister):
    """
    Class which implements common functionality for all
    registers, which are used to calculate amount of
    resource used.
    """

    def __init__(self, fit, usage_attr):
        self.__usage_attr = usage_attr
        self.__resource_users = set()
        fit._subscribe(self, self._handler_map.keys())

    def _register_item(self, item):
        if self.__usage_attr not in item._eve_type.attributes:
            return
        self.__resource_users.add(item)

    def _unregister_item(self, item):
        self.__resource_users.discard(item)

    def get_resource_use(self):
        # Calculate resource consumption of all items on ship
        return sum(item.attributes[self.__usage_attr] for item in self.__resource_users)


class CpuUseRegister(ResourceUseRegister):
    """
    Details:
    Only items with online effect active and cpu attribute
    on eve item are tracked.
    """

    def __init__(self, fit):
        ResourceUseRegister.__init__(self, fit, Attribute.cpu)

    def _handle_item_effects_activation(self, message):
        if Effect.online in message.effects:
            ResourceUseRegister._register_item(self, message.item)

    def _handle_item_effects_deactivation(self, message):
        if Effect.online in message.effects:
            ResourceUseRegister._unregister_item(self, message.item)

    _handler_map = {
        InstrEffectsActivate: _handle_item_effects_activation,
        InstrEffectsDeactivate: _handle_item_effects_deactivation
    }

    def get_resource_use(self):
        return round(ResourceUseRegister.get_resource_use(self), 2)


class PowerGridUseRegister(ResourceUseRegister):
    """
    Details:
    Only items with online effect active and power attribute
    on eve item are tracked.
    """

    def __init__(self, fit):
        ResourceUseRegister.__init__(self, fit, Attribute.power)

    def _handle_item_effects_activation(self, message):
        if Effect.online in message.effects:
            ResourceUseRegister._register_item(self, message.item)

    def _handle_item_effects_deactivation(self, message):
        if Effect.online in message.effects:
            ResourceUseRegister._unregister_item(self, message.item)

    _handler_map = {
        InstrEffectsActivate: _handle_item_effects_activation,
        InstrEffectsDeactivate: _handle_item_effects_deactivation
    }

    def get_resource_use(self):
        return round(ResourceUseRegister.get_resource_use(self), 2)


class CalibrationUseRegister(ResourceUseRegister):
    """
    Details:
    Only items with rig slot effect active and upgrade cost attribute
    on eve item are tracked.
    """

    def __init__(self, fit):
        ResourceUseRegister.__init__(self, fit, Attribute.upgrade_cost)

    def _handle_item_effects_activation(self, message):
        if Effect.rig_slot in message.effects:
            ResourceUseRegister._register_item(self, message.item)

    def _handle_item_effects_deactivation(self, message):
        if Effect.rig_slot in message.effects:
            ResourceUseRegister._unregister_item(self, message.item)

    _handler_map = {
        InstrEffectsActivate: _handle_item_effects_activation,
        InstrEffectsDeactivate: _handle_item_effects_deactivation
    }


class DroneBayVolumeUseRegister(ResourceUseRegister):
    """
    Details:
    Only items of Drone class with volume attribute on eve type are tracked.
    """

    def __init__(self, fit):
        ResourceUseRegister.__init__(self, fit, Attribute.volume)

    def _handle_item_addition(self, message):
        if isinstance(message.item, Drone):
            ResourceUseRegister._register_item(self, message.item)

    def _handle_item_removal(self, message):
        if isinstance(message.item, Drone):
            ResourceUseRegister._unregister_item(self, message.item)

    _handler_map = {
        InstrItemAdd: _handle_item_addition,
        InstrItemRemove: _handle_item_removal
    }


class DroneBandwidthUseRegister(ResourceUseRegister):
    """
    Details:
    Only items of Drone class with bandwidth attribute on eve type are tracked.
    """

    def __init__(self, fit):
        ResourceUseRegister.__init__(self, fit, Attribute.drone_bandwidth_used)

    def _handle_item_states_activation(self, message):
        if isinstance(message.item, Drone) and State.online in message.states:
            ResourceUseRegister._register_item(self, message.item)

    def _handle_item_states_deactivation(self, message):
        if isinstance(message.item, Drone) and State.online in message.states:
            ResourceUseRegister._unregister_item(self, message.item)

    _handler_map = {
        InstrStatesActivate: _handle_item_states_activation,
        InstrStatesDeactivate: _handle_item_states_deactivation
    }
