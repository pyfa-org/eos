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
from eos.fit.restrictionTracker.exception import CpuException, PowerGridException, CalibrationException, \
DroneBayVolumeException, DroneBandwidthException
from eos.fit.restrictionTracker.registerAbc import RestrictionRegister


class ResourceRegister(RestrictionRegister):
    """
    Class which implements common functionality for all
    registers, which track amount of resource, which is
    used by items belonging to ship, and produced
    by ship itself.
    """

    def __init__(self, fit, outputAttr, usageAttr, exceptionClass):
        self._fit = fit
        # On ship holder, attribute with this ID
        # contains total amount of produced resource
        self.__outputAttr = outputAttr
        # On holders, attribute with this ID contains
        # amount of used resource as value
        self.__usageAttr = usageAttr
        self.__exceptionClass = exceptionClass
        # Container for holders which use resource
        # Format: {holders}
        self.__resourceUsers = set()

    def registerHolder(self, holder):
        # Do not process holders, whose base items don't
        # use resource
        if not self.__usageAttr in holder.item.attributes:
            return
        self.__resourceUsers.add(holder)

    def unregisterHolder(self, holder):
        self.__resourceUsers.discard(holder)

    def validate(self):
        # Get ship's resource output, setting it to 0
        # if fitting doesn't have ship assigned,
        # or ship doesn't have resource output attribute
        shipHolder = self._fit.ship
        try:
            shipHolderAttribs = shipHolder.attributes
        except AttributeError:
            resourceOutput = 0
        else:
            try:
                resourceOutput = shipHolderAttribs[self.__outputAttr]
            except KeyError:
                resourceOutput = 0
        # Calculate resource consumption of all holders on ship
        totalResourceConsumption = 0
        # Also use the same loop to compose set of holders,
        # which actually consume resource (have positive non-null
        # usage)
        resourceConsumers = set()
        for resourceUser in self.__resourceUsers:
            resourceUse = resourceUser.attributes[self.__usageAttr]
            totalResourceConsumption += resourceUse
            if resourceUse > 0:
                resourceConsumers.add(resourceUser)
        # If we're out of resource, raise error
        # with holders-resource-consumers
        if totalResourceConsumption > resourceOutput:
            raise self.__exceptionClass(resourceConsumers)


class CpuRegister(ResourceRegister):
    """
    Implements restriction:
    CPU usage by holders should not exceed ship CPU output.

    Details:
    For validation, modified values of CPU usage and
    CPU output are taken.
    """

    def __init__(self, fit):
        ResourceRegister.__init__(self, fit, Attribute.cpuOutput, Attribute.cpu, CpuException)


class PowerGridRegister(ResourceRegister):
    """
    Implements restriction:
    Power grid usage by holders should not exceed ship
    power grid output.

    Details:
    For validation, modified values of power grid usage and
    power grid output are taken.
    """

    def __init__(self, fit):
        ResourceRegister.__init__(self, fit, Attribute.powerOutput, Attribute.power, PowerGridException)


class CalibrationRegister(ResourceRegister):
    """
    Implements restriction:
    Calibration usage by holders should not exceed ship
    calibration output.

    Details:
    For validation, modified values of calibration usage and
    calibration output are taken.
    """

    def __init__(self, fit):
        ResourceRegister.__init__(self, fit, Attribute.upgradeCapacity, Attribute.upgradeCost, CalibrationException)


class DroneBayVolumeRegister(ResourceRegister):
    """
    Implements restriction:
    Drone bay volume usage by holders should not exceed ship
    drone bay volume.

    Details:
    Only holders located in drone container are tracked.
    For validation, modified values of drone bay volume usage and
    drone bay volume are taken.
    """

    def __init__(self, fit):
        ResourceRegister.__init__(self, fit, Attribute.droneCapacity, Attribute.volume, DroneBayVolumeException)

    def registerHolder(self, holder):
        if not holder in self._fit.drones:
            return
        ResourceRegister.registerHolder(self, holder)


class DroneBandwidthRegister(ResourceRegister):
    """
    Implements restriction:
    Drone bandwidth usage by holders should not exceed ship
    drone bandwidth output.

    Details:
    For validation, modified values of drone bandwidth usage and
    drone bandwidth output are taken.
    """

    def __init__(self, fit):
        ResourceRegister.__init__(self, fit, Attribute.droneBandwidth, Attribute.droneBandwidthUsed, DroneBandwidthException)
