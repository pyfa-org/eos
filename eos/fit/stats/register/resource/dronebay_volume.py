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


from eos.const.eve import AttrId
from eos.fit.item import Drone
from eos.fit.message import ItemLoaded
from eos.fit.message import ItemUnloaded
from .base import BaseResourceRegister


class DronebayVolumeRegister(BaseResourceRegister):

    def __init__(self, fit):
        BaseResourceRegister.__init__(self)
        self.__fit = fit
        self.__resource_users = set()
        fit._subscribe(self, self._handler_map.keys())

    @property
    def used(self):
        return sum(item.attrs[AttrId.volume] for item in self.__resource_users)

    @property
    def output(self):
        try:
            return self.__fit.ship.attrs[AttrId.drone_capacity]
        except (AttributeError, KeyError):
            return 0

    @property
    def _users(self):
        return self.__resource_users

    def _handle_item_loaded(self, msg):
        if (
            isinstance(msg.item, Drone) and
            AttrId.volume in msg.item._type_attrs
        ):
            self.__resource_users.add(msg.item)

    def _handle_item_unloaded(self, msg):
        if isinstance(msg.item, Drone):
            self.__resource_users.discard(msg.item)

    _handler_map = {
        ItemLoaded: _handle_item_loaded,
        ItemUnloaded: _handle_item_unloaded}
