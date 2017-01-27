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


from eos.const.eve import Attribute
from eos.fit.item import Drone
from .base import BaseStatRegister


class ResourceUseRegister(BaseStatRegister):
    """
    Class which implements common functionality for all
    registers, which are used to calculate amount of
    resource used.
    """

    def __init__(self, usage_attr):
        self.__usage_attr = usage_attr
        self.__resource_users = set()

    def register_item(self, item):
        if self.__usage_attr not in item._eve_type.attributes:
            return
        self.__resource_users.add(item)

    def unregister_item(self, item):
        self.__resource_users.discard(item)

    def get_resource_use(self):
        # Calculate resource consumption of all items on ship
        return sum(h.attributes[self.__usage_attr] for h in self.__resource_users)


class CpuUseRegister(ResourceUseRegister):

    def __init__(self):
        ResourceUseRegister.__init__(self, Attribute.cpu)

    def get_resource_use(self):
        return round(ResourceUseRegister.get_resource_use(self), 2)


class PowerGridUseRegister(ResourceUseRegister):

    def __init__(self):
        ResourceUseRegister.__init__(self, Attribute.power)

    def get_resource_use(self):
        return round(ResourceUseRegister.get_resource_use(self), 2)


class CalibrationUseRegister(ResourceUseRegister):

    def __init__(self):
        ResourceUseRegister.__init__(self, Attribute.upgrade_cost)


class DroneBayVolumeUseRegister(ResourceUseRegister):
    """
    Details:
    Only items of Drone class are tracked.
    """

    def __init__(self):
        ResourceUseRegister.__init__(self, Attribute.volume)

    def register_item(self, item):
        if isinstance(item, Drone):
            ResourceUseRegister.register_item(self, item)


class DroneBandwidthUseRegister(ResourceUseRegister):

    def __init__(self):
        ResourceUseRegister.__init__(self, Attribute.drone_bandwidth_used)
