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


from eos.const.eve import Attribute
from eos.fit.item import Ship, Drone
from eos.fit.pubsub.message import InstrItemAdd, InstrItemRemove
from eos.util.volatile_cache import InheritableVolatileMixin, volatile_property
from .base import BaseResourceStatRegister


class DronebayVolumeStatRegister(BaseResourceStatRegister, InheritableVolatileMixin):

    def __init__(self, msg_broker):
        BaseResourceStatRegister.__init__(self)
        InheritableVolatileMixin.__init__(self)
        self.__current_ship = None
        self.__resource_users = set()
        msg_broker._subscribe(self, self._handler_map.keys())

    @volatile_property
    def used(self):
        return sum(item.attributes[Attribute.volume] for item in self.__resource_users)

    @volatile_property
    def output(self):
        try:
            ship_attribs = self.__current_ship.attributes
        except AttributeError:
            return None
        else:
            try:
                return ship_attribs[Attribute.drone_capacity]
            except KeyError:
                return None

    @property
    def _users(self):
        return self.__resource_users

    def _handle_item_addition(self, message):
        if isinstance(message.item, Drone) and Attribute.volume in message.item._eve_type.attributes:
            self.__resource_users.add(message.item)
        elif isinstance(message.item, Ship):
            self.__current_ship = message.item

    def _handle_item_removal(self, message):
        if isinstance(message.item, Drone):
            self.__resource_users.discard(message.item)
        elif message.item is self.__current_ship:
            self.__current_ship = None

    _handler_map = {
        InstrItemAdd: _handle_item_addition,
        InstrItemRemove: _handle_item_removal
    }
