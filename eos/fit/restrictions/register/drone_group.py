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


from collections import namedtuple

from eos.const.eos import Restriction
from eos.const.eve import Attribute
from eos.fit.item import Drone
from .base import BaseRestrictionRegister
from ..exception import RegisterValidationError


RESTRICTION_ATTRS = (
    Attribute.allowed_drone_group_1,
    Attribute.allowed_drone_group_2
)


DroneGroupErrorData = namedtuple('DroneGroupErrorData', ('item_group', 'allowed_groups'))


class DroneGroupRestrictionRegister(BaseRestrictionRegister):
    """
    Implements restriction:
    If ship restricts drone group, items from groups which are not
    allowed cannot be put into drone bay.

    Details:
    Only items of Drone class are tracked.
    For validation, allowedDroneGroupX attribute values of eve type
    are taken.
    Validation fails if ship's eve type has any restriction attribute,
    and drone group doesn't match to restriction.
    """

    def __init__(self, fit):
        self._fit = fit
        # Container for items which can be subject
        # for restriction
        # Format: {items}
        self.__restricted_items = set()

    def register_item(self, item):
        # Ignore everything but drones
        if isinstance(item, Drone):
            self.__restricted_items.add(item)

    def unregister_item(self, item):
        self.__restricted_items.discard(item)

    def validate(self):
        ship_item = self._fit.ship
        # No ship - no restriction
        try:
            ship_eve_type = ship_item._eve_type
        except AttributeError:
            return
        # Set with allowed groups
        allowed_groups = set()
        # Find out if we have restriction, and which drone groups it allows
        for restriction_attr in RESTRICTION_ATTRS:
            allowed_groups.add(ship_eve_type.attributes.get(restriction_attr))
        allowed_groups.discard(None)
        # No allowed group attributes - no restriction
        if not allowed_groups:
            return
        tainted_items = {}
        # Convert set to tuple, this way we can use it
        # multiple times in error data, making sure that
        # it can't be modified by validation caller
        allowed_groups = tuple(allowed_groups)
        for item in self.__restricted_items:
            # Taint items, whose group is not allowed
            item_group = item._eve_type.group
            if item_group not in allowed_groups:
                tainted_items[item] = DroneGroupErrorData(
                    item_group=item_group,
                    allowed_groups=allowed_groups
                )
        if tainted_items:
            raise RegisterValidationError(tainted_items)

    @property
    def restriction_type(self):
        return Restriction.drone_group
