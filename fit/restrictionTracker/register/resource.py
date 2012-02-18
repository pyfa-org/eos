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


from eos.const import Location
from eos.eve.const import Attribute
from eos.fit.restrictionTracker.exception import CpuException
from eos.fit.restrictionTracker.registerAbc import RestrictionRegister


class ResourceRegister(RestrictionRegister):
    """
    Class which implements common functionality for all
    registers, which track amount of resource, which is
    used by items belonging to ship, and produced
    by ship itself.
    """

    def __init__(self, fit, usageAttr, outputAttr, exceptionClass):
        self.__fit = fit
        # On holders, attribute with this ID contains
        # amount of used resource as value
        self.__usageAttr = usageAttr
        # On ship holder, attribute with this ID
        # contains total amount of produced resource
        self.__outputAttr = outputAttr
        self.__exceptionClass = exceptionClass
        # Container for holders which use resource
        # Format: {holders}
        self.__resourceUsers = set()

    def registerHolder(self, holder):
        # Ignore holders which do not belong to ship
        if holder._location != Location.ship:
            return
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
        shipHolder = self.__fit.ship
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
    CPU usage by ship holders should not exceed ship CPU output.

    Details:
    Only holders belonging to ship are tracked.
    For validation, modified values of CPU usage and
    CPU output are taken.
    """

    def __init__(self, fit):
        ResourceRegister.__init__(self, fit, Attribute.cpu, Attribute.cpuOutput, CpuException)
        self.__fit = fit
