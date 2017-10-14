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


import math

from eos.const.eve import AttributeId
from eos.fit.helper import DamageTypes, TankingLayers, TankingLayersTotal
from eos.fit.item import Ship
from eos.fit.pubsub.message import InstrItemAdd, InstrItemRemove
from eos.fit.pubsub.subscriber import BaseSubscriber
from eos.util.volatile_cache import InheritableVolatileMixin, volatile_property
from .register import *


class StatService(BaseSubscriber, InheritableVolatileMixin):
    """Object which is used as access points for all fit statistics.

    Args:
        msg_broker: Message broker which is used to deliver all the messages
            about context changes.
    """

    def __init__(self, msg_broker):
        BaseSubscriber.__init__(self)
        InheritableVolatileMixin.__init__(self)
        self.__current_ship = None
        self.__dd_reg = DamageDealerRegister(msg_broker)
        # Initialize sub-containers
        self.cpu = CpuStatRegister(msg_broker)
        self.powergrid = PowergridStatRegister(msg_broker)
        self.calibration = CalibrationStatRegister(msg_broker)
        self.dronebay = DronebayVolumeStatRegister(msg_broker)
        self.drone_bandwidth = DroneBandwidthStatRegister(msg_broker)
        self.high_slots = HighSlotStatRegister(msg_broker)
        self.med_slots = MediumSlotStatRegister(msg_broker)
        self.low_slots = LowSlotStatRegister(msg_broker)
        self.rig_slots = RigSlotStatRegister(msg_broker)
        self.subsystem_slots = SubsystemSlotStatRegister(msg_broker)
        self.turret_slots = TurretSlotStatRegister(msg_broker)
        self.launcher_slots = LauncherSlotStatRegister(msg_broker)
        self.launched_drones = LaunchedDroneStatRegister(msg_broker)
        self.__volatile_containers = (
            self.cpu,
            self.powergrid,
            self.calibration,
            self.dronebay,
            self.drone_bandwidth,
            self.high_slots,
            self.med_slots,
            self.low_slots,
            self.rig_slots,
            self.subsystem_slots,
            self.turret_slots,
            self.launcher_slots,
            self.launched_drones
        )
        msg_broker._subscribe(self, self._handler_map.keys())

    @volatile_property
    def hp(self):
        """Fetch ship HP stats.

        Returns: TankingLayersTotal helper container instance. If ship data
        cannot be fetched, HP values will be None.
        """
        try:
            return self.__current_ship.hp
        except AttributeError:
            return TankingLayersTotal(hull=None, armor=None, shield=None)

    @volatile_property
    def resistances(self):
        """Fetch ship resistances.

        Returns: TankingLayers helper container instance, whose attributes are
        DamageTypes helper container instances. If ship data cannot be fetched,
        resistance values will be None.
        """
        try:
            return self.__current_ship.resistances
        except AttributeError:
            empty = DamageTypes(
                em=None, thermal=None, kinetic=None, explosive=None)
            return TankingLayers(hull=empty, armor=empty, shield=empty)

    def get_ehp(self, damage_profile=None):
        """Get effective HP of an item against passed damage profile.

        Args:
            damage_profile (optional): DamageProfile helper container instance.
                If not specified, default on-fit damage profile is used.

        Returns: TankingLayersTotal helper container instance. If ship data
        cannot be fetched, EHP values will be None.
        """
        try:
            return self.__current_ship.get_ehp(damage_profile)
        except AttributeError:
            return TankingLayersTotal(hull=None, armor=None, shield=None)

    @volatile_property
    def worst_case_ehp(self):
        """Get eve-style effective HP for the item.

        Eve takes the worst resistance and calculates EHP against it, on a per-
        layer basis.

        Returns: TankingLayersTotal helper container instance. If ship data
        cannot be fetched, EHP values will be None.
        """
        try:
            return self.__current_ship.worst_case_ehp
        except AttributeError:
            return TankingLayersTotal(hull=None, armor=None, shield=None)

    def get_nominal_volley(self, item_filter=None, target_resistances=None):
        """
        Get nominal volley of the fit.

        Args:
            item_filter (optional): When iterating over fit items, this function
                is called. If evaluated as True, this item is taken into
                consideration, else not. If argument is None, all items 'pass
                filter'. By default None.
            target_resistances (optional): ResistanceProfile helper container
                instance. If specified, effective damage against these
                resistances is calculated.

        Returns: DamageTypesTotal helper container instance.
        """
        volley = self.__dd_reg._collect_damage_stats(
            item_filter,
            'get_nominal_volley',
            target_resistances=target_resistances
        )
        return volley

    def get_nominal_dps(
        self, item_filter=None, target_resistances=None, reload=False
    ):
        """
        Get nominal DPS of the fit.

        Args:
            item_filter (optional): When iterating over fit items, this function
                is called. If evaluated as True, this item is taken into
                consideration, else not. If argument is None, all items 'pass
                filter'. By default None.
            target_resistances (optional): ResistanceProfile helper container
                instance. If specified, effective damage against these
                resistances is calculated.
            reload (optional): Boolean flag which controls if reload should be
                taken into consideration or not. By default, reload is ignored.

        Returns: DamageTypesTotal helper container instance.
        """
        dps = self.__dd_reg._collect_damage_stats(
            item_filter,
            'get_nominal_dps',
            target_resistances=target_resistances,
            reload=reload
        )
        return dps

    @volatile_property
    def agility_factor(self):
        try:
            ship_attribs = self.__current_ship.attributes
        except AttributeError:
            return None
        try:
            agility = ship_attribs[AttributeId.agility]
            mass = ship_attribs[AttributeId.mass]
        except KeyError:
            return None
        real_agility = -math.log(0.25) * agility * mass / 1000000
        return real_agility

    @volatile_property
    def align_time(self):
        try:
            return math.ceil(self.agility_factor)
        except TypeError:
            return None

    def _clear_volatile_attrs(self):
        """Clear volatile cache for self and all child objects."""
        for container in self.__volatile_containers:
            container._clear_volatile_attrs()
        InheritableVolatileMixin._clear_volatile_attrs(self)

    def _handle_item_addition(self, message):
        if isinstance(message.item, Ship):
            self.__current_ship = message.item

    def _handle_item_removal(self, message):
        if message.item is self.__current_ship:
            self.__current_ship = None

    _handler_map = {
        InstrItemAdd: _handle_item_addition,
        InstrItemRemove: _handle_item_removal
    }
