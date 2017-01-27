# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2017 Anton Vorobyov
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
from .base import BaseRestrictionRegister
from ..exception import RegisterValidationError


ResourceErrorData = namedtuple('ResourceErrorData', ('total_use', 'output', 'item_use'))


class ResourceRestrictionRegister(BaseRestrictionRegister):
    """
    Class which implements common functionality for all
    registers, which track amount of resource, which is
    used by various fit items.
    """

    def __init__(self, fit, stat_name, usage_attr, restriction_type):
        self.__restriction_type = restriction_type
        self._fit = fit
        # Use this stat name to get numbers from stats service
        self.__stat_name = stat_name
        self.__usage_attr = usage_attr
        self.__resource_users = set()

    def register_item(self, item):
        if self.__usage_attr not in item._eve_type.attributes:
            return
        self.__resource_users.add(item)

    def unregister_item(self, item):
        self.__resource_users.discard(item)

    def validate(self):
        # Use stats module to get resource use and output
        stats = getattr(self._fit.stats, self.__stat_name)
        total_use = stats.used
        # Can be None, so fall back to 0 in this case
        output = stats.output or 0
        # If we're not out of resource, do nothing
        if total_use <= output:
            return
        tainted_items = {}
        for item in self.__resource_users:
            resource_use = item.attributes[self.__usage_attr]
            # Ignore items which do not actually
            # consume resource
            if resource_use <= 0:
                continue
            tainted_items[item] = ResourceErrorData(
                total_use=total_use,
                output=output,
                item_use=resource_use
            )
        raise RegisterValidationError(tainted_items)

    @property
    def restriction_type(self):
        return self.__restriction_type


class CpuRegister(ResourceRestrictionRegister):
    """
    Implements restriction:
    CPU usage by items should not exceed ship CPU output.

    Details:
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        ResourceRestrictionRegister.__init__(self, fit, 'cpu', Attribute.cpu, Restriction.cpu)


class PowerGridRegister(ResourceRestrictionRegister):
    """
    Implements restriction:
    Power grid usage by items should not exceed ship
    power grid output.

    Details:
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        ResourceRestrictionRegister.__init__(self, fit, 'powergrid', Attribute.power, Restriction.powergrid)


class CalibrationRegister(ResourceRestrictionRegister):
    """
    Implements restriction:
    Calibration usage by items should not exceed ship
    calibration output.

    Details:
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        ResourceRestrictionRegister.__init__(self, fit, 'calibration', Attribute.upgrade_cost, Restriction.calibration)


class DroneBayVolumeRegister(ResourceRestrictionRegister):
    """
    Implements restriction:
    Drone bay volume usage by items should not exceed ship
    drone bay volume.

    Details:
    Only items placed to fit.drones are tracked.
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        ResourceRestrictionRegister.__init__(self, fit, 'dronebay', Attribute.volume, Restriction.dronebay_volume)

    def register_item(self, item):
        if item in self._fit.drones:
            ResourceRestrictionRegister.register_item(self, item)


class DroneBandwidthRegister(ResourceRestrictionRegister):
    """
    Implements restriction:
    Drone bandwidth usage by items should not exceed ship
    drone bandwidth output.

    Details:
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        ResourceRestrictionRegister.__init__(self, fit, 'drone_bandwidth', Attribute.drone_bandwidth_used,
                                             Restriction.drone_bandwidth)
