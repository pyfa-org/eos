# ==============================================================================
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
# ==============================================================================


from collections import namedtuple

from eos.const.eos import Restriction
from eos.const.eve import AttributeId
from .base import BaseRestriction
from ..exception import RestrictionValidationError


ResourceErrorData = namedtuple(
    'ResourceErrorData', ('total_use', 'output', 'item_use'))


class ResourceRestriction(BaseRestriction):
    """Base class for all resource restrictions.

    Resources in this context is something produced by ship/character and
    consumed by other items.
    """

    def __init__(self, stats, stat_name, use_attr_id):
        self.__stats = stats
        # Use this stat name to get numbers from stats service
        self.__stat_name = stat_name
        self.__use_attr_id = use_attr_id

    def validate(self):
        # Use stats module to get resource use and output
        stats = getattr(self.__stats, self.__stat_name)
        total_use = stats.used
        # Can be None, so fall back to 0 in this case
        output = stats.output or 0
        # If we're not out of resource, do nothing
        if total_use <= output:
            return
        tainted_items = {}
        for item in stats._users:
            resource_use = item.attributes[self.__use_attr_id]
            # Ignore items which do not actually consume resource
            if resource_use <= 0:
                continue
            tainted_items[item] = ResourceErrorData(
                total_use=total_use,
                output=output,
                item_use=resource_use)
        raise RestrictionValidationError(tainted_items)


class CpuRestriction(ResourceRestriction):
    """CPU use by items should not exceed ship CPU output.

    Details:
        For validation, stats module data is used.
    """

    def __init__(self, stats):
        ResourceRestriction.__init__(
            self, stats, 'cpu', AttributeId.cpu)

    @property
    def type(self):
        return Restriction.cpu


class PowergridRestriction(ResourceRestriction):
    """Power grid use by items should not exceed ship power grid output.

    Details:
        For validation, stats module data is used.
    """

    def __init__(self, stats):
        ResourceRestriction.__init__(
            self, stats, 'powergrid', AttributeId.power)

    @property
    def type(self):
        return Restriction.powergrid


class CalibrationRestriction(ResourceRestriction):
    """Calibration use by items should not exceed ship calibration output.

    Details:
        For validation, stats module data is used.
    """

    def __init__(self, stats):
        ResourceRestriction.__init__(
            self, stats, 'calibration', AttributeId.upgrade_cost)

    @property
    def type(self):
        return Restriction.calibration


class DroneBayVolumeRestriction(ResourceRestriction):
    """Drone bay volume use by items should not exceed ship drone bay volume.

    Details:
        For validation, stats module data is used.
    """

    def __init__(self, stats):
        ResourceRestriction.__init__(
            self, stats, 'dronebay', AttributeId.volume)

    @property
    def type(self):
        return Restriction.dronebay_volume


class DroneBandwidthRestriction(ResourceRestriction):
    """Drone bandwidth use by items should not exceed ship drone bandwidth.

    Details:
        For validation, stats module data is used.
    """

    def __init__(self, stats):
        ResourceRestriction.__init__(
            self, stats, 'drone_bandwidth', AttributeId.drone_bandwidth_used)

    @property
    def type(self):
        return Restriction.drone_bandwidth
