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


from collections import namedtuple

from eos.const.eos import Restriction
from eos.const.eve import AttributeId
from eos.fit.item import Drone, Ship
from eos.fit.pubsub.message import InstrItemAdd, InstrItemRemove
from .base import BaseRestrictionRegister
from ..exception import RestrictionValidationError


RESTRICTION_ATTRS = (
    AttributeId.allowed_drone_group_1,
    AttributeId.allowed_drone_group_2)


DroneGroupErrorData = namedtuple(
    'DroneGroupErrorData', ('drone_group', 'allowed_groups'))


class DroneGroupRestrictionRegister(BaseRestrictionRegister):
    """Do not allow to use drones besides those specified by ship.

    Details:
        Only items of Drone class are tracked.
        For validation, allowedDroneGroupX attribute values of eve type are
            taken.
        If ship specifies no drone group preference, validation always passes.
    """

    def __init__(self, msg_broker):
        self.__current_ship = None
        self.__drones = set()
        msg_broker._subscribe(self, self._handler_map.keys())

    def _handle_item_addition(self, message):
        if isinstance(message.item, Ship):
            self.__current_ship = message.item
        elif isinstance(message.item, Drone):
            self.__drones.add(message.item)

    def _handle_item_removal(self, message):
        if message.item is self.__current_ship:
            self.__current_ship = None
        self.__drones.discard(message.item)

    _handler_map = {
        InstrItemAdd: _handle_item_addition,
        InstrItemRemove: _handle_item_removal}

    def validate(self):
        ship = self.__current_ship
        # No ship - no restriction
        if ship is None:
            return
        allowed_groups = []
        # Find out if we have restriction, and which drone groups it allows
        for restriction_attr in RESTRICTION_ATTRS:
            try:
                restriction_value = ship._eve_type_attributes[restriction_attr]
            except KeyError:
                continue
            else:
                allowed_groups.append(restriction_value)
        # No allowed group attributes - no restriction
        if not allowed_groups:
            return
        tainted_items = {}
        # Convert set to tuple, this way we can use it multiple times in error
        # data, making sure that it can't be modified by validation caller
        allowed_groups = tuple(allowed_groups)
        for drone in self.__drones:
            # Taint items, whose group is not allowed
            drone_group = drone._eve_type.group
            if drone_group not in allowed_groups:
                tainted_items[drone] = DroneGroupErrorData(
                    drone_group=drone_group,
                    allowed_groups=allowed_groups)
        if tainted_items:
            raise RestrictionValidationError(tainted_items)

    @property
    def type(self):
        return Restriction.drone_group
