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


from eos.const.eve import Attribute
from eos.fit.statTracker.register import StatRegister
from eos.fit.statTracker.container import Resource


class ResourceRegister(StatRegister):
    """
    Class which implements common functionality for all
    registers, which track amount of resource, which is
    used by items belonging to ship, and produced
    by ship itself.
    """

    def __init__(self, fit, outputAttr, usageAttr):
        self._fit = fit
        # On ship holder, attribute with this ID
        # contains total amount of produced resource
        self.__outputAttr = outputAttr
        # On holders, attribute with this ID contains
        # amount of used resource as value
        self.__usageAttr = usageAttr
        # Container for holders which use resource
        # Format: {holders}
        self.__resourceUsers = set()

    def registerHolder(self, holder):
        if self.__usageAttr not in holder.item.attributes:
            return
        self.__resourceUsers.add(holder)

    def unregisterHolder(self, holder):
        self.__resourceUsers.discard(holder)

    def getResourceStats(self):
        # Get ship's resource output, setting it to None
        # if fitting doesn't have ship assigned,
        # or ship doesn't have resource output attribute
        shipHolder = self._fit.ship
        try:
            shipHolderAttribs = shipHolder.attributes
        except AttributeError:
            output = None
        else:
            try:
                output = shipHolderAttribs[self.__outputAttr]
            except KeyError:
                output = None
        # Calculate resource consumption of all holders on ship
        consumption = sum(h.attributes[self.__usageAttr] for h in self.__resourceUsers)
        return Resource(used=consumption, output=output)

class CpuRegister(ResourceRegister):
    """
    Implements restriction:
    CPU usage by holders should not exceed ship CPU output.

    Details:
    For validation, modified values of CPU usage and
    CPU output are taken. Absence of ship or absence of
    required attribute on ship are considered as zero output.
    """

    def __init__(self, fit):
        ResourceRegister.__init__(self, fit, Attribute.cpuOutput, Attribute.cpu)
