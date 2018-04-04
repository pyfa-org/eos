# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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


from abc import ABCMeta
from abc import abstractmethod
from collections import namedtuple

from eos.const.eos import Restriction
from eos.const.eve import AttrId
from eos.restriction.exception import RestrictionValidationError
from .base import BaseRestriction


ResourceErrorData = namedtuple(
    'ResourceErrorData', ('total_use', 'output', 'item_use'))


class ResourceRestriction(BaseRestriction, metaclass=ABCMeta):
    """Base class for all resource restrictions.

    Resources in this context is something produced by ship/character and
    consumed by other items.
    """

    def __init__(self, fit):
        self.__fit = fit

    @property
    @abstractmethod
    def _stat_name(self):
        """This name will be used to get numbers from stats service."""
        ...

    @property
    @abstractmethod
    def _use_attr_id(self):
        ...

    def validate(self):
        # Use stats module to get resource use and output
        stats = getattr(self.__fit.stats, self._stat_name)
        total_use = stats.used
        # Can be None, so fall back to 0 in this case
        output = stats.output or 0
        # If we're not out of resource, do nothing
        if total_use <= output:
            return
        tainted_items = {}
        for item in stats._users:
            resource_use = item.attrs[self._use_attr_id]
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

    type = Restriction.cpu
    _stat_name = 'cpu'
    _use_attr_id = AttrId.cpu


class PowergridRestriction(ResourceRestriction):
    """Power grid use by items should not exceed ship power grid output.

    Details:
        For validation, stats module data is used.
    """

    type = Restriction.powergrid
    _stat_name = 'powergrid'
    _use_attr_id = AttrId.power


class CalibrationRestriction(ResourceRestriction):
    """Calibration use by items should not exceed ship calibration output.

    Details:
        For validation, stats module data is used.
    """

    type = Restriction.calibration
    _stat_name = 'calibration'
    _use_attr_id = AttrId.upgrade_cost


class DroneBayVolumeRestriction(ResourceRestriction):
    """Drone bay volume use by items should not exceed ship drone bay volume.

    Details:
        For validation, stats module data is used.
    """

    type = Restriction.dronebay_volume
    _stat_name = 'dronebay'
    _use_attr_id = AttrId.volume


class DroneBandwidthRestriction(ResourceRestriction):
    """Drone bandwidth use by items should not exceed ship drone bandwidth.

    Details:
        For validation, stats module data is used.
    """

    type = Restriction.drone_bandwidth
    _stat_name = 'drone_bandwidth'
    _use_attr_id = AttrId.drone_bandwidth_used
