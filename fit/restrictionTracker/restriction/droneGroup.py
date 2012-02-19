#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2012 Anton Vorobyov
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


from eos.eve.const import Attribute
from eos.fit.restrictionTracker.exception import DroneGroupException
from eos.fit.restrictionTracker.register import RestrictionRegister


class DroneGroupRegister(RestrictionRegister):
    """
    Implements restriction:
    If ship restricts drone group, holders from groups which are not
    allowed cannot be put into drone bay.

    Details:
    Only holders located in drone container are tracked.
    If holder has at least one restriction attribute, it is enabled
    for tracking by this register. Please note that None-values of
    attributes enable restriction, but do not allow to fit holder to
    any ship, even if its type or group are None.
    For validation, original values of allowedDroneGroupX attributes
    are taken.
    """

    def __init__(self, tracker):
        self._tracker = tracker
        # Container for holders which can be subject
        # for restriction
        # Format: {holders}
        self.__restrictableHolders = set()

    def registerHolder(self, holder):
        # Ignore everything but drones
        if not holder in self._tracker._fit.drones:
            return
        self.__restrictableHolders.add(holder)

    def unregisterHolder(self, holder):
        self.__restrictableHolders.discard(holder)

    def validate(self):
        shipHolder = self._tracker._fit.ship
        # No ship - no restriction
        try:
            shipItem = shipHolder.item
        except AttributeError:
            return
        # Flag which describes if ship restricts
        # drone groups, and set with allowed groups
        droneRestriction = False
        allowedGroups = set()
        # Find out if we have restriction, and which drone groups it allowes
        for restrictionAttr in (Attribute.allowedDroneGroup1, Attribute.allowedDroneGroup2):
            if restrictionAttr in shipItem.attributes:
                droneRestriction = True
                allowedGroup = shipItem.attributes[restrictionAttr]
                if allowedGroup is not None:
                    allowedGroups.add(allowedGroup)
        # No restriction attributes - no restriction,
        # obviously
        if droneRestriction is not True:
            return
        taintedHolders = set()
        for restrictedHolder in self.__restrictableHolders:
            # NTaint holders, whose group is not allowed
            holderGroup = restrictedHolder.item.groupId
            if not holderGroup in allowedGroups:
                taintedHolders.add(restrictedHolder)
        if len(taintedHolders) > 0:
            raise DroneGroupException(taintedHolders)
