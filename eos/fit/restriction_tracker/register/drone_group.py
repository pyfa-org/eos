# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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
from eos.fit.holder.item import Drone
from eos.fit.restriction_tracker.exception import RegisterValidationError
from .abc import RestrictionRegister


RESTRICTION_ATTRS = (
    Attribute.allowed_drone_group_1,
    Attribute.allowed_drone_group_2
)


DroneGroupErrorData = namedtuple('DroneGroupErrorData', ('holder_group', 'allowed_groups'))


class DroneGroupRegister(RestrictionRegister):
    """
    Implements restriction:
    If ship restricts drone group, holders from groups which are not
    allowed cannot be put into drone bay.

    Details:
    Only holders of Drone class are tracked.
    For validation, original values of allowedDroneGroupX attributes
    are taken. Validation fails if ship's original attributes have
    any restriction attribute, and drone group doesn't match to
    restriction.
    """

    def __init__(self, fit):
        self._fit = fit
        # Container for holders which can be subject
        # for restriction
        # Format: {holders}
        self.__restricted_holders = set()

    def register_holder(self, holder):
        # Ignore everything but drones
        if isinstance(holder, Drone):
            self.__restricted_holders.add(holder)

    def unregister_holder(self, holder):
        self.__restricted_holders.discard(holder)

    def validate(self):
        ship_holder = self._fit.ship
        # No ship - no restriction
        try:
            ship_item = ship_holder.item
        except AttributeError:
            return
        # Set with allowed groups
        allowed_groups = set()
        # Find out if we have restriction, and which drone groups it allows
        for restriction_attr in RESTRICTION_ATTRS:
            allowed_groups.add(ship_item.attributes.get(restriction_attr))
        allowed_groups.discard(None)
        # No allowed group attributes - no restriction
        if not allowed_groups:
            return
        tainted_holders = {}
        # Convert set to tuple, this way we can use it
        # multiple times in error data, making sure that
        # it can't be modified by validation caller
        allowed_groups = tuple(allowed_groups)
        for holder in self.__restricted_holders:
            # Taint holders, whose group is not allowed
            holder_group = holder.item.group
            if holder_group not in allowed_groups:
                tainted_holders[holder] = DroneGroupErrorData(
                    holder_group=holder_group,
                    allowed_groups=allowed_groups
                )
        if tainted_holders:
            raise RegisterValidationError(tainted_holders)

    @property
    def restriction_type(self):
        return Restriction.drone_group
