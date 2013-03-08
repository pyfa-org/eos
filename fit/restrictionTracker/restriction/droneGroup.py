#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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
#===============================================================================


from collections import namedtuple

from eos.const.eos import Restriction
from eos.const.eve import Attribute
from eos.fit.restrictionTracker.exception import RegisterValidationError
from eos.fit.restrictionTracker.register import RestrictionRegister


DroneGroupErrorData = namedtuple('DroneGroupErrorData', ('allowedGroups', 'droneGroup'))


class DroneGroupRegister(RestrictionRegister):
    """
    Implements restriction:
    If ship restricts drone group, holders from groups which are not
    allowed cannot be put into drone bay.

    Details:
    Only holders located in drone container are tracked.
    For validation, original values of allowedDroneGroupX attributes
    are taken. Validation fails if ship's original attributes have
    any restriction attribute, and drone group doesn't match to
    restriction.
    """

    def __init__(self, tracker):
        self._tracker = tracker
        # Container for holders which can be subject
        # for restriction
        # Format: {holders}
        self.__restrictedHolders = set()

    def registerHolder(self, holder):
        # Ignore everything but drones
        if not holder in self._tracker._fit.drones:
            return
        self.__restrictedHolders.add(holder)

    def unregisterHolder(self, holder):
        self.__restrictedHolders.discard(holder)

    def validate(self):
        shipHolder = self._tracker._fit.ship
        # No ship - no restriction
        try:
            shipItem = shipHolder.item
        except AttributeError:
            return
        # Set with allowed groups
        allowedGroups = set()
        # Find out if we have restriction, and which drone groups it allows
        for restrictionAttr in (Attribute.allowedDroneGroup1, Attribute.allowedDroneGroup2):
            try:
                allowedGroup = shipItem.attributes[restrictionAttr]
            except KeyError:
                continue
            allowedGroups.add(allowedGroup)
        # No allowed group attributes - no restriction
        if not allowedGroups:
            return
        taintedHolders = {}
        # Convert set to tuple, this way we can use it
        # multiple times in error data, making sure that
        # it can't be modified by validation caller
        allowedGroups = tuple(allowedGroups)
        for holder in self.__restrictedHolders:
            # Taint holders, whose group is not allowed
            holderGroup = holder.item.groupId
            if not holderGroup in allowedGroups:
                taintedHolders[holder] = DroneGroupErrorData(allowedGroups=allowedGroups,
                                                             droneGroup=holderGroup)
        if taintedHolders:
            raise RegisterValidationError(taintedHolders)

    @property
    def restrictionType(self):
        return Restriction.droneGroup
