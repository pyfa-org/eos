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


from eos.const.eos import State
from eos.const.eve import AttrId
from eos.fit.item import Drone, Ship
from eos.fit.message import (
    ItemAdded, ItemRemoved, StatesActivated, StatesDeactivated)
from eos.util.volatile_cache import InheritableVolatileMixin, volatile_property
from .base import BaseResourceStatRegister


class DroneBandwidthStatRegister(
        BaseResourceStatRegister, InheritableVolatileMixin):

    def __init__(self, msg_broker):
        BaseResourceStatRegister.__init__(self)
        InheritableVolatileMixin.__init__(self)
        self.__current_ship = None
        self.__resource_users = set()
        msg_broker._subscribe(self, self._handler_map.keys())

    @volatile_property
    def used(self):
        return sum(
            item.attrs[AttrId.drone_bandwidth_used]
            for item in self.__resource_users)

    @volatile_property
    def output(self):
        try:
            return self.__current_ship.attrs[AttrId.drone_bandwidth]
        except (AttributeError, KeyError):
            return None

    @property
    def _users(self):
        return self.__resource_users

    def _handle_item_added(self, msg):
        if isinstance(msg.item, Ship):
            self.__current_ship = msg.item

    def _handle_item_removed(self, msg):
        if msg.item is self.__current_ship:
            self.__current_ship = None

    def _handle_states_activated(self, msg):
        if (
            isinstance(msg.item, Drone) and
            State.online in msg.states and
            AttrId.drone_bandwidth_used in msg.item._type_attrs
        ):
            self.__resource_users.add(msg.item)

    def _handle_states_deactivated(self, msg):
        if isinstance(msg.item, Drone) and State.online in msg.states:
            self.__resource_users.discard(msg.item)

    _handler_map = {
        ItemAdded: _handle_item_added,
        ItemRemoved: _handle_item_removed,
        StatesActivated: _handle_states_activated,
        StatesDeactivated: _handle_states_deactivated}
