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
from eos.fit.holder.item import Drone
from eos.fit.restrictionTracker.exception import RegisterValidationError
from eos.fit.restrictionTracker.register import RestrictionRegister


ResourceErrorData = namedtuple('ResourceErrorData', ('output', 'totalUse', 'holderUse'))


class ResourceRegister(RestrictionRegister):
    """
    Class which implements common functionality for all
    registers, which track amount of resource, which is
    used by items belonging to ship, and produced
    by ship itself.
    """

    def __init__(self, fit, statName, usageAttr, restrictionType):
        self.__restrictionType = restrictionType
        self._fit = fit
        # Use this resource name to get numbers
        # from stats tracker
        self.__statName = statName
        # On holders, attribute with this ID contains
        # amount of used resource as value
        self.__usageAttr = usageAttr
        # Container for holders which use resource
        # Format: {holders}
        self.__resourceUsers = set()

    def registerHolder(self, holder):
        # Do not process holders, whose base items don't
        # use resource
        if self.__usageAttr not in holder.item.attributes:
            return
        self.__resourceUsers.add(holder)

    def unregisterHolder(self, holder):
        self.__resourceUsers.discard(holder)

    def validate(self):
        # Use stats module to get resource use and output
        stats = getattr(self._fit.stats, self.__statName)
        totalUse = stats.used
        # Can be None, so fall back to 0 in this case
        output = stats.output or 0
        # If we're out of resource, raise error
        # with holders-resource-consumers
        if totalUse > output:
            taintedHolders = {}
            for holder in self.__resourceUsers:
                resourceUse = holder.attributes[self.__usageAttr]
                if resourceUse > 0:
                    taintedHolders[holder] = ResourceErrorData(output=output,
                                                               totalUse=totalUse,
                                                               holderUse=resourceUse)
            raise RegisterValidationError(taintedHolders)

    @property
    def restrictionType(self):
        return self.__restrictionType


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
        ResourceRegister.__init__(self, fit, 'cpu', Attribute.cpu, Restriction.cpu)


class PowerGridRegister(ResourceRegister):
    """
    Implements restriction:
    Power grid usage by holders should not exceed ship
    power grid output.

    Details:
    For validation, modified values of power grid usage and
    power grid output are taken. Absence of ship or absence of
    required attribute on ship are considered as zero output.
    """

    def __init__(self, fit):
        ResourceRegister.__init__(self, fit, 'powerGrid', Attribute.power, Restriction.powerGrid)


class CalibrationRegister(ResourceRegister):
    """
    Implements restriction:
    Calibration usage by holders should not exceed ship
    calibration output.

    Details:
    For validation, modified values of calibration usage and
    calibration output are taken. Absence of ship or absence of
    required attribute on ship are considered as zero output.
    """

    def __init__(self, fit):
        ResourceRegister.__init__(self, fit, 'calibration', Attribute.upgradeCost, Restriction.calibration)


class DroneBayVolumeRegister(ResourceRegister):
    """
    Implements restriction:
    Drone bay volume usage by holders should not exceed ship
    drone bay volume.

    Details:
    Only holders of Drone class are tracked.
    For validation, modified values of drone bay volume usage and
    drone bay volume are taken. Absence of ship or absence of
    required attribute on ship are considered as zero output.
    """

    def __init__(self, fit):
        ResourceRegister.__init__(self, fit, 'droneBay', Attribute.volume, Restriction.droneBayVolume)

    def registerHolder(self, holder):
        if isinstance(holder, Drone):
            ResourceRegister.registerHolder(self, holder)


class DroneBandwidthRegister(ResourceRegister):
    """
    Implements restriction:
    Drone bandwidth usage by holders should not exceed ship
    drone bandwidth output.

    Details:
    For validation, modified values of drone bandwidth usage and
    drone bandwidth output are taken. Absence of ship or absence of
    required attribute on ship are considered as zero output.
    """

    def __init__(self, fit):
        ResourceRegister.__init__(self, fit, 'droneBandwidth', Attribute.droneBandwidthUsed, Restriction.droneBandwidth)
