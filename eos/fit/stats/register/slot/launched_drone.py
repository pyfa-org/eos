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
from eos.fit.item import Drone
from eos.fit.message import StatesActivated
from eos.fit.message import StatesDeactivated
from .base import BaseSlotRegister


class LaunchedDroneRegister(BaseSlotRegister):

    def __init__(self, fit):
        BaseSlotRegister.__init__(self)
        self.__fit = fit
        self.__drones = set()
        fit._subscribe(self, self._handler_map.keys())

    @property
    def used(self):
        return len(self.__drones)

    @property
    def total(self):
        try:
            return int(self.__fit.character.attrs[AttrId.max_active_drones])
        except (AttributeError, KeyError):
            return 0

    @property
    def _users(self):
        return self.__drones

    def _handle_states_activated(self, msg):
        if isinstance(msg.item, Drone) and State.online in msg.states:
            self.__drones.add(msg.item)

    def _handle_states_deactivated(self, msg):
        if isinstance(msg.item, Drone) and State.online in msg.states:
            self.__drones.discard(msg.item)

    _handler_map = {
        StatesActivated: _handle_states_activated,
        StatesDeactivated: _handle_states_deactivated}
