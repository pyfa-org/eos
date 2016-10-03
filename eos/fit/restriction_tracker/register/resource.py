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
from eos.fit.restriction_tracker.exception import RegisterValidationError
from .abc import RestrictionRegister


ResourceErrorData = namedtuple('ResourceErrorData', ('total_use', 'output', 'holder_use'))


class ResourceRegister(RestrictionRegister):
    """
    Class which implements common functionality for all
    registers, which track amount of resource, which is
    used by various fit holders.
    """

    def __init__(self, fit, stat_name, usage_attr, restriction_type):
        self.__restriction_type = restriction_type
        self._fit = fit
        # Use this stat name to get numbers from stats tracker
        self.__stat_name = stat_name
        self.__usage_attr = usage_attr
        self.__resource_users = set()

    def register_holder(self, holder):
        if self.__usage_attr not in holder.item.attributes:
            return
        self.__resource_users.add(holder)

    def unregister_holder(self, holder):
        self.__resource_users.discard(holder)

    def validate(self):
        # Use stats module to get resource use and output
        stats = getattr(self._fit.stats, self.__stat_name)
        total_use = stats.used
        # Can be None, so fall back to 0 in this case
        output = stats.output or 0
        # If we're not out of resource, do nothing
        if total_use <= output:
            return
        tainted_holders = {}
        for holder in self.__resource_users:
            resource_use = holder.attributes[self.__usage_attr]
            # Ignore holders which do not actually
            # consume resource
            if resource_use <= 0:
                continue
            tainted_holders[holder] = ResourceErrorData(
                total_use=total_use,
                output=output,
                holder_use=resource_use
            )
        raise RegisterValidationError(tainted_holders)

    @property
    def restriction_type(self):
        return self.__restriction_type


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
        ResourceRegister.__init__(self, fit, 'powergrid', Attribute.power, Restriction.powergrid)


class CalibrationRegister(ResourceRegister):
    """
    Implements restriction:
    Calibration usage by holders should not exceed ship
    calibration output.

    Details:
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        ResourceRegister.__init__(self, fit, 'calibration', Attribute.upgrade_cost, Restriction.calibration)


class DroneBayVolumeRegister(ResourceRegister):
    """
    Implements restriction:
    Drone bay volume usage by holders should not exceed ship
    drone bay volume.

    Details:
    Only holders placed to fit.drones are tracked.
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        ResourceRegister.__init__(self, fit, 'dronebay', Attribute.volume, Restriction.dronebay_volume)

    def register_holder(self, holder):
        if holder in self._fit.drones:
            ResourceRegister.register_holder(self, holder)


class DroneBandwidthRegister(ResourceRegister):
    """
    Implements restriction:
    Drone bandwidth usage by holders should not exceed ship
    drone bandwidth output.

    Details:
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        ResourceRegister.__init__(self, fit, 'drone_bandwidth', Attribute.drone_bandwidth_used,
                                  Restriction.drone_bandwidth)
