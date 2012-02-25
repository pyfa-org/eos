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


from collections import namedtuple

from eos.const import Restriction
from eos.eve.const import Attribute
from eos.fit.restrictionTracker.exception import RegisterValidationError
from eos.fit.restrictionTracker.register import RestrictionRegister


LaunchedDroneErrorData = namedtuple("LaunchedDroneErrorData", ("maxLaunchedDrones", "launchedDrones"))


class LaunchedDroneRegister(RestrictionRegister):
    """
    Implements restriction:
    Number of simultaneously used drones cannot exceed number of
    drones character is able to control.

    Details:
    Only holders located in drone container are tracked.
    For validation, modified value of maxActiveDrones attribute
    is taken.
    """

    def __init__(self, tracker):
        self._tracker = tracker
        # Container for holders which are considered
        # as in-space drones
        # Format: {holders}
        self.__restrictedHolders = set()

    def registerHolder(self, holder):
        # Register only drones
        if not holder in self._tracker._fit.drones:
            return
        self.__restrictedHolders.add(holder)

    def unregisterHolder(self, holder):
        self.__restrictedHolders.discard(holder)

    def validate(self):
        # Get number of drones fit can have in space; assign
        # it to None if fitting doesn't have character, or
        # attribute isn't available
        characterHolder = self._tracker._fit.character
        try:
            characterHolderAttribs = characterHolder.attributes
        except AttributeError:
            maxLaunchedDrones = 0
        else:
            try:
                maxLaunchedDrones = characterHolderAttribs[Attribute.maxActiveDrones]
            except KeyError:
                maxLaunchedDrones = 0
        # If number of registered drones exceeds number of maximum number
        # of allowed drones, raise error
        if len(self.__restrictedHolders) > maxLaunchedDrones:
            taintedHolders = {}
            launchedDrones = len(self.__restrictedHolders)
            for holder in self.__restrictedHolders:
                taintedHolders[holder] = LaunchedDroneErrorData(maxLaunchedDrones=maxLaunchedDrones,
                                                                launchedDrones=launchedDrones)
            raise RegisterValidationError(taintedHolders)

    @property
    def restrictionType(self):
        return Restriction.launchedDrone
