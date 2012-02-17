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
from eos.fit.attributeCalculator.exception import NoAttributeException
from eos.fit.restrictionTracker.exception import CpuException
from eos.fit.restrictionTracker.registerAbc import RestrictionRegister


class CpuRegister(RestrictionRegister):
    """
    Implements restriction:
    CPU usage by holders should not exceed CPU output.

    Details:
    Only holders belonging to ship are tracked.
    For validation, modified values of CPU usage and
    CPU output are taken.
    """

    def __init__(self, fit):
        self.__fit = fit
        # Container for registered holders
        # Format: {cpu consumers}
        self.__cpuUsers = set()

    def registerHolder(self, holder):
        # Ignore holders which do not belong to ship
        if holder._location != Location.ship:
            return
        # Do not process holders, whose base items don't
        # consume cpu
        if not Attribute.cpu in holder.item.attributes:
            return
        # Add holder to container
        self.__cpuUsers.add(holder)

    def unregisterHolder(self, holder):
        # Remove holder from container, if it's there
        self.__cpuUsers.discard(holder)

    def validate(self):
        # Get ship's CPU output, setting it to 0
        # if fitting doesn't have ship assigned,
        # or ship doesn't have cpu output attribute
        shipHolder = self.__fit.ship
        try:
            shipHolderAttribs = shipHolder.attributes
        except AttributeError:
            cpuOutput = 0
        else:
            try:
                cpuOutput = shipHolderAttribs[Attribute.cpuOutput]
            except NoAttributeException:
                cpuOutput = 0
        # Calculate CPU consumption of all holders on ship
        totalCpuConsumption = 0
        # Also use the same loop to compose set of holders,
        # which actually consume CPU
        cpuConsumers = set()
        for cpuUser in self.__cpuUsers:
            cpuUse = cpuUser.attributes[Attribute.cpu]
            totalCpuConsumption += cpuUse
            if cpuUse > 0:
                cpuConsumers.add(cpuUser)
        # If fitting is out of CPU, raise error
        # with holders-cpu-consumers
        if totalCpuConsumption > cpuOutput:
            raise CpuException(cpuConsumers)
