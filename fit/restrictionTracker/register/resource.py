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
from .abc import RestrictionRegister


ResourceErrorData = namedtuple('ResourceErrorData', ('output', 'totalUse', 'holderUse'))


class ResourceRegister(RestrictionRegister):
    """
    Class which implements common functionality for all
    registers, which track amount of resource, which is
    used by various fit holders.
    """

    def __init__(self, fit, statName, usageAttr, restrictionType):
        self.__restrictionType = restrictionType
        self._fit = fit
        # Use this resource name to get numbers from stats tracker
        self.__statName = statName
        self.__usageAttr = usageAttr
        self.__resourceUsers = set()

    def registerHolder(self, holder):
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
        # If we're not out of resource, do nothing
        if totalUse <= output:
            return
        taintedHolders = {}
        for holder in self.__resourceUsers:
            resourceUse = holder.attributes[self.__usageAttr]
            # Ignore holders which do not actually
            # consume resource
            if resourceUse <= 0:
                continue
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
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        ResourceRegister.__init__(self, fit, 'cpu', Attribute.cpu, Restriction.cpu)


class PowerGridRegister(ResourceRegister):
    """
    Implements restriction:
    Power grid usage by holders should not exceed ship
    power grid output.

    Details:
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        ResourceRegister.__init__(self, fit, 'powerGrid', Attribute.power, Restriction.powerGrid)


class CalibrationRegister(ResourceRegister):
    """
    Implements restriction:
    Calibration usage by holders should not exceed ship
    calibration output.

    Details:
    For validation, stats module data is used.
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
    For validation, stats module data is used.
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
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        ResourceRegister.__init__(self, fit, 'droneBandwidth', Attribute.droneBandwidthUsed, Restriction.droneBandwidth)
