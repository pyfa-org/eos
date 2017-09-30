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


from eos.const.eve import Attribute, Effect
from eos.fit.item import Ship
from eos.fit.pubsub.message import InstrEffectsStart, InstrEffectsStop, InstrItemAdd, InstrItemRemove
from eos.util.volatile_cache import InheritableVolatileMixin, volatile_property
from .base import BaseSlotStatRegister


class OrderedShipSlotStatRegister(BaseSlotStatRegister, InheritableVolatileMixin):

    def __init__(self, msg_broker, slot_effect, slot_attr):
        BaseSlotStatRegister.__init__(self)
        InheritableVolatileMixin.__init__(self)
        self.__slot_effect = slot_effect
        self.__slot_attr = slot_attr
        self.__current_ship = None
        self.__slot_users = set()
        msg_broker._subscribe(self, self._handler_map.keys())

    @volatile_property
    def used(self):
        return max((
            i._container_position + 1 for i in self.__slot_users if i._container_position is not None
        ), default=0)

    @volatile_property
    def total(self):
        try:
            ship_attribs = self.__current_ship.attributes
        except AttributeError:
            return None
        else:
            try:
                return int(ship_attribs[self.__slot_attr])
            except KeyError:
                return None

    @property
    def _users(self):
        return self.__slot_users

    def _handle_item_addition(self, message):
        if isinstance(message.item, Ship):
            self.__current_ship = message.item

    def _handle_item_removal(self, message):
        if message.item is self.__current_ship:
            self.__current_ship = None

    def _handle_item_effects_activation(self, message):
        if self.__slot_effect in message.effects:
            self.__slot_users.add(message.item)

    def _handle_item_effects_deactivation(self, message):
        if self.__slot_effect in message.effects:
            self.__slot_users.discard(message.item)

    _handler_map = {
        InstrItemAdd: _handle_item_addition,
        InstrItemRemove: _handle_item_removal,
        InstrEffectsStart: _handle_item_effects_activation,
        InstrEffectsStop: _handle_item_effects_deactivation
    }


class HighSlotStatRegister(OrderedShipSlotStatRegister):

    def __init__(self, msg_broker):
        OrderedShipSlotStatRegister.__init__(self, msg_broker, Effect.hi_power, Attribute.hi_slots)


class MediumSlotStatRegister(OrderedShipSlotStatRegister):

    def __init__(self, msg_broker):
        OrderedShipSlotStatRegister.__init__(self, msg_broker, Effect.med_power, Attribute.med_slots)


class LowSlotStatRegister(OrderedShipSlotStatRegister):

    def __init__(self, msg_broker):
        OrderedShipSlotStatRegister.__init__(self, msg_broker, Effect.lo_power, Attribute.low_slots)
