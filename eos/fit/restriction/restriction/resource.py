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
from eos.const.eve import Attribute, Effect
from eos.fit.item import Drone
from eos.fit.pubsub.message import InstrEffectsActivate, InstrEffectsDeactivate
from .base import BaseRestriction
from ..exception import RestrictionValidationError


ResourceErrorData = namedtuple('ResourceErrorData', ('total_use', 'output', 'item_use'))


class ResourceRestriction(BaseRestriction):
    """
    Class which implements common functionality for all
    registers, which track amount of resource, which is
    used by various fit items.
    """

    def __init__(self, stats, stat_name, usage_attr, restriction_type):
        self.__restriction_type = restriction_type
        self.__stats = stats
        # Use this stat name to get numbers from stats service
        self.__stat_name = stat_name
        self.__usage_attr = usage_attr
        self.__resource_users = set()

    def _register_item(self, item):
        if self.__usage_attr not in item._eve_type.attributes:
            return
        self.__resource_users.add(item)

    def _unregister_item(self, item):
        self.__resource_users.discard(item)

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
        raise RestrictionValidationError(tainted_items)

    @property
    def type(self):
        return self.__restriction_type


class CpuRestriction(ResourceRestriction):
    """
    Implements restriction:
    CPU usage by items should not exceed ship CPU output.

    Details:
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        ResourceRestriction.__init__(self, fit.stats, 'cpu', Attribute.cpu, Restriction.cpu)
        fit._subscribe(self, self._handler_map.keys())

    def _handle_item_effects_activation(self, message):
        if Effect.online in message.effects:
            ResourceRestriction._register_item(self, message.item)

    def _handle_item_effects_deactivation(self, message):
        if Effect.online in message.effects:
            ResourceRestriction._unregister_item(self, message.item)

    _handler_map = {
        InstrEffectsActivate: _handle_item_effects_activation,
        InstrEffectsDeactivate: _handle_item_effects_deactivation
    }


class PowerGridRestriction(ResourceRestriction):
    """
    Implements restriction:
    Power grid usage by items should not exceed ship
    power grid output.

    Details:
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        ResourceRestriction.__init__(self, fit, 'powergrid', Attribute.power, Restriction.powergrid)


class CalibrationRestriction(ResourceRestriction):
    """
    Implements restriction:
    Calibration usage by items should not exceed ship
    calibration output.

    Details:
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        ResourceRestriction.__init__(self, fit, 'calibration', Attribute.upgrade_cost, Restriction.calibration)


class DroneBayVolumeRestriction(ResourceRestriction):
    """
    Implements restriction:
    Drone bay volume usage by items should not exceed ship
    drone bay volume.

    Details:
    Only items of Drone class are restricted.
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        ResourceRestriction.__init__(self, fit, 'dronebay', Attribute.volume, Restriction.dronebay_volume)

    def register_item(self, item):
        if isinstance(item, Drone):
            ResourceRestriction._register_item(self, item)


class DroneBandwidthRestriction(ResourceRestriction):
    """
    Implements restriction:
    Drone bandwidth usage by items should not exceed ship
    drone bandwidth output.

    Details:
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        ResourceRestriction.__init__(
            self, fit, 'drone_bandwidth', Attribute.drone_bandwidth_used, Restriction.drone_bandwidth
        )
