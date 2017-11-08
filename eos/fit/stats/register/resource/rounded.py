# ==============================================================================
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
# ==============================================================================


from eos.const.eve import AttributeId, EffectId
from eos.fit.item import Ship
from eos.fit.pubsub.message import (
    EffectsStarted, EffectsStopped, ItemAdded, ItemRemoved)
from eos.util.volatile_cache import InheritableVolatileMixin, volatile_property
from .base import BaseResourceStatRegister


class RoundedResourceStatRegister(
        BaseResourceStatRegister, InheritableVolatileMixin):

    def __init__(self, msg_broker, output_attr_id, use_effect_id, use_attr_id):
        BaseResourceStatRegister.__init__(self)
        InheritableVolatileMixin.__init__(self)
        self.__output_attr_id = output_attr_id
        self.__use_effect_id = use_effect_id
        self.__use_attr_id = use_attr_id
        self.__current_ship = None
        self.__resource_users = set()
        msg_broker._subscribe(self, self._handler_map.keys())

    @volatile_property
    def used(self):
        return round(sum(
            item.attributes[self.__use_attr_id]
            for item in self.__resource_users), 2)

    @volatile_property
    def output(self):
        try:
            return self.__current_ship.attributes[self.__output_attr_id]
        except (AttributeError, KeyError):
            return None

    @property
    def _users(self):
        return self.__resource_users

    def _handle_item_addition(self, message):
        if isinstance(message.item, Ship):
            self.__current_ship = message.item

    def _handle_item_removal(self, message):
        if message.item is self.__current_ship:
            self.__current_ship = None

    def _handle_item_effects_activation(self, message):
        if (
            self.__use_effect_id in message.effect_ids and
            self.__use_attr_id in message.item._type_attributes
        ):
            self.__resource_users.add(message.item)

    def _handle_item_effects_deactivation(self, message):
        if self.__use_effect_id in message.effect_ids:
            self.__resource_users.discard(message.item)

    _handler_map = {
        ItemAdded: _handle_item_addition,
        ItemRemoved: _handle_item_removal,
        EffectsStarted: _handle_item_effects_activation,
        EffectsStopped: _handle_item_effects_deactivation}


class CpuStatRegister(RoundedResourceStatRegister):

    def __init__(self, msg_broker):
        RoundedResourceStatRegister.__init__(
            self, msg_broker, AttributeId.cpu_output, EffectId.online,
            AttributeId.cpu)


class PowergridStatRegister(RoundedResourceStatRegister):

    def __init__(self, msg_broker):
        RoundedResourceStatRegister.__init__(
            self, msg_broker, AttributeId.power_output, EffectId.online,
            AttributeId.power)
