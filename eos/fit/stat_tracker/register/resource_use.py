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


from eos.const.eve import Attribute
from .abc import StatRegister


class ResourceUseRegister(StatRegister):
    """
    Class which implements common functionality for all
    registers, which are used to calculate amount of
    resource used.
    """

    def __init__(self, fit, usage_attr):
        self._fit = fit
        self.__usage_attr = usage_attr
        self.__resource_users = set()

    def register_holder(self, holder):
        if self.__usage_attr not in holder.item.attributes:
            return
        self.__resource_users.add(holder)

    def unregister_holder(self, holder):
        self.__resource_users.discard(holder)

    def get_resource_use(self):
        # Calculate resource consumption of all holders on ship
        return sum(h.attributes[self.__usage_attr] for h in self.__resource_users)


class CpuUseRegister(ResourceUseRegister):
    """Calculates CPU use of passed fit."""

    def __init__(self, fit):
        ResourceUseRegister.__init__(self, fit, Attribute.cpu)

    def get_resource_use(self):
        return round(ResourceUseRegister.get_resource_use(self), 2)


class PowerGridUseRegister(ResourceUseRegister):
    """Calculates powergrid use of passed fit."""

    def __init__(self, fit):
        ResourceUseRegister.__init__(self, fit, Attribute.power)

    def get_resource_use(self):
        return round(ResourceUseRegister.get_resource_use(self), 2)


class CalibrationUseRegister(ResourceUseRegister):
    """Calculates calibration use of passed fit."""

    def __init__(self, fit):
        ResourceUseRegister.__init__(self, fit, Attribute.upgrade_cost)


class DroneBayVolumeUseRegister(ResourceUseRegister):
    """
    Calculates drone bay used on passed fit.

    Details:
    Only holders of Drone class are tracked.
    """

    def __init__(self, fit):
        ResourceUseRegister.__init__(self, fit, Attribute.volume)

    def register_holder(self, holder):
        if holder in self._fit.drones:
            ResourceUseRegister.register_holder(self, holder)


class DroneBandwidthUseRegister(ResourceUseRegister):
    """Calculates drone bandwidth use of passed fit."""

    def __init__(self, fit):
        ResourceUseRegister.__init__(self, fit, Attribute.drone_bandwidth_used)
