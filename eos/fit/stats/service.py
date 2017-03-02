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


import math

from eos.const.eos import State
from eos.const.eve import Attribute
from eos.fit.message import ItemAdded, ItemRemoved, ItemStateChanged, EnableServices, DisableServices
from eos.fit.helper import DamageTypes, TankingLayers, TankingLayersTotal
from eos.util.pubsub import BaseSubscriber
from eos.util.volatile_cache import InheritableVolatileMixin, volatile_property
from .container import *
from .register import *


class StatService(InheritableVolatileMixin, BaseSubscriber):
    """
    Object which is used as access points for all
    fit statistics.

    Required arguments:
    fit -- Fit object to which service is assigned
    """

    def __init__(self, fit):
        InheritableVolatileMixin.__init__(self)
        BaseSubscriber.__init__(self)
        self.__enabled = False
        self._fit = fit
        # Initialize registers
        cpu_reg = CpuUseRegister()
        powergrid_reg = PowerGridUseRegister()
        calibration_reg = CalibrationUseRegister()
        dronebay_reg = DroneBayVolumeUseRegister()
        drone_bandwidth_reg = DroneBandwidthUseRegister()
        turret_reg = TurretUseRegister(fit)
        launcher_reg = LauncherUseRegister(fit)
        launched_drone_reg = LaunchedDroneRegister(fit)
        self._dd_reg = DamageDealerRegister()
        # List of registers which do not rely on item state
        # Format: (register,)
        self.__regs_stateless = (
            calibration_reg,
            dronebay_reg,
            turret_reg,
            launcher_reg
        )
        # Dictionary which keeps stat registers which
        # use item state as some input/condition
        # Format: {triggering state: {registers}}
        self.__regs_stateful = {
            State.offline: (
                self._dd_reg,
            ),
            State.online: (
                cpu_reg,
                powergrid_reg,
                drone_bandwidth_reg,
                launched_drone_reg
            )
        }
        # Initialize sub-containers
        self.cpu = ShipResource(fit, cpu_reg, Attribute.cpu_output)
        self.powergrid = ShipResource(fit, powergrid_reg, Attribute.power_output)
        self.calibration = ShipResource(fit, calibration_reg, Attribute.upgrade_capacity)
        self.dronebay = ShipResource(fit, dronebay_reg, Attribute.drone_capacity)
        self.drone_bandwidth = ShipResource(fit, drone_bandwidth_reg, Attribute.drone_bandwidth)
        self.high_slots = ShipSlots(fit, fit.modules.high, Attribute.hi_slots)
        self.med_slots = ShipSlots(fit, fit.modules.med, Attribute.med_slots)
        self.low_slots = ShipSlots(fit, fit.modules.low, Attribute.low_slots)
        self.rig_slots = ShipSlots(fit, fit.rigs, Attribute.rig_slots)
        self.subsystem_slots = ShipSlots(fit, fit.subsystems, Attribute.subsystem_slot)
        self.turret_slots = ShipSlots(fit, turret_reg, Attribute.turret_slots_left)
        self.launcher_slots = ShipSlots(fit, launcher_reg, Attribute.launcher_slots_left)
        self.launched_drones = CharSlots(fit, launched_drone_reg, Attribute.max_active_drones)
        self._volatile_containers = (
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
        fit._subscribe(self, self._handler_map.keys())

    @volatile_property
    def hp(self):
        """
        Fetch current ship HP and return object with hull, armor, shield and
        total attributes. If fit has no ship or some data cannot be fetched,
        corresponding attribs will be set to None.
        """
        ship_item = self._fit.ship
        try:
            hp_data = ship_item.hp
        except AttributeError:
            return TankingLayersTotal(hull=None, armor=None, shield=None)
        else:
            # Build tuple here because the object we fetched
            # from ship is access point to stats, which are
            # updated on fit changes
            return TankingLayersTotal(
                hull=hp_data.hull,
                armor=hp_data.armor,
                shield=hp_data.shield
            )

    @volatile_property
    def resistances(self):
        """
        Fetch current ship resistances and return object wit following data:
        .hull.em, .hull.thermal, .hull.kinetic, .hull.explosive,
        .armor.em, .armor.thermal, .armor.kinetic, .armor.explosive,
        .shield.em, .shield.thermal, .shield.kinetic, .shield.explosive
        If fit has no ship or some data cannot be fetched, corresponding attribs
        will be set to None.
        """
        ship_item = self._fit.ship
        try:
            return ship_item.resistances
        except AttributeError:
            empty = DamageTypes(em=None, thermal=None, kinetic=None, explosive=None)
            return TankingLayers(hull=empty, armor=empty, shield=empty)

    def get_ehp(self, damage_profile=None):
        """
        Same as hp, but takes damage_profile argument which optionally defines
        damage profile (should have em, thermal, kinetic and explosive arguments
        defined as numbers). Returns effective HP of a ship against this profile.
        If fit has no ship or some data cannot be fetched, corresponding attribs
        will be set to None. If no profile is specified, default fit profile is
        taken.
        """
        ship_item = self._fit.ship
        try:
            return ship_item.get_ehp(damage_profile)
        except AttributeError:
            return TankingLayersTotal(hull=None, armor=None, shield=None)

    @volatile_property
    def worst_case_ehp(self):
        """
        Eve-style EHP for a ship - calculated using worst resistance for each layer.
        If fit has no ship or some data cannot be fetched, corresponding attribs
        will be set to None.
        """
        ship_item = self._fit.ship
        try:
            return ship_item.worst_case_ehp
        except AttributeError:
            return TankingLayersTotal(hull=None, armor=None, shield=None)

    def get_nominal_volley(self, item_filter=None, target_resistances=None):
        """
        Get nominal volley of whole fit.

        Optional arguments:
        item_filter -- when iterating over fit item, this function is called.
        If evaluated as True, this item is taken into consideration, else not.
        If argument is None, all items 'pass filter'. By default None.
        target_resistances -- resistance profile to calculate effective volley.
        Profile should contain em, thermal, kinetic and explosive attributes as
        numbers in range [0..1]. If None, 'raw' dps is calculated. By default None.

        Return value:
        Object with em, thermal, kinetic, explosive and total attributes.
        """
        volley = self._dd_reg._collect_damage_stats(
            item_filter,
            'get_nominal_volley',
            target_resistances=target_resistances
        )
        return volley

    def get_nominal_dps(self, item_filter=None, target_resistances=None, reload=False):
        """
        Get nominal dps of whole fit.

        Optional arguments:
        item_filter -- when iterating over fit item, this function is called.
        If evaluated as True, this item is taken into consideration, else not.
        If argument is None, all items 'pass filter'. By default None.
        target_resistances -- resistance profile to calculate effective dps.
        Profile should contain em, thermal, kinetic and explosive attributes as
        numbers in range [0..1]. If None, 'raw' dps is calculated. By default None.
        reload -- boolean flag, should reload be taken into consideration or not.
        By default False.

        Return value:
        Object with em, thermal, kinetic, explosive and total attributes.
        """
        dps = self._dd_reg._collect_damage_stats(
            item_filter,
            'get_nominal_dps',
            target_resistances=target_resistances,
            reload=reload
        )
        return dps

    @volatile_property
    def agility_factor(self):
        ship_item = self._fit.ship
        try:
            ship_attribs = ship_item.attributes
        except AttributeError:
            return None
        try:
            agility = ship_attribs[Attribute.agility]
            mass = ship_attribs[Attribute.mass]
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
        """
        Clear volatile cache for self and all child objects.
        """
        for container in self._volatile_containers:
            container._clear_volatile_attrs()
        InheritableVolatileMixin._clear_volatile_attrs(self)

    # Message handling
    def _handle_item_addition(self, message):
        if not self.__enabled:
            return
        self.__add_item(message.item)

    def _handle_item_removal(self, message):
        if not self.__enabled:
            return
        self.__remove_item(message.item)

    def _handle_item_state_change(self, message):
        if not self.__enabled:
            return
        item, old_state, new_state = message
        if new_state > old_state:
            states = set(filter(lambda s: old_state < s <= new_state, State))
            self.__enable_states(item, states)
        elif new_state < old_state:
            states = set(filter(lambda s: new_state < s <= old_state, State))
            self.__disable_states(item, states)

    def _handle_enable_services(self, message):
        """
        Enable service and register passed items.
        """
        self.__enabled = True
        for item in message.items:
            self.__add_item(item)

    def _handle_disable_services(self, message):
        """
        Unregister passed items from this service and
        disable it.
        """
        for item in message.items:
            self.__remove_item(item)

    _handler_map = {
        ItemAdded: _handle_item_addition,
        ItemRemoved: _handle_item_removal,
        ItemStateChanged: _handle_item_state_change,
        EnableServices: _handle_enable_services,
        DisableServices: _handle_disable_services
    }

    def _notify(self, message):

        try:
            handler = self._handler_map[type(message)]
        except KeyError:
            return
        handler(self, message)

    # Private methods for message handlers
    def __add_item(self, item):
        for register in self.__regs_stateless:
            register.register_item(item)
        states = set(filter(lambda s: s <= item.state, State))
        self.__enable_states(item, states)

    def __remove_item(self, item):
        states = set(filter(lambda s: s <= item.state, State))
        self.__disable_states(item, states)
        for register in self.__regs_stateless:
            register.unregister_item(item)

    def __enable_states(self, item, states):
        """
        Handle state switch upwards.

        Required arguments:
        item -- item, for which states are switched
        states -- iterable with states, which are passed
            during state switch, except for initial state
        """
        for state in states:
            # Not all states have corresponding registers,
            # just skip those which don't
            try:
                registers = self.__regs_stateful[state]
            except KeyError:
                continue
            for register in registers:
                register.register_item(item)

    def __disable_states(self, item, states):
        """
        Handle state switch downwards.

        Required arguments:
        item -- item, for which states are switched
        states -- iterable with states, which are passed
            during state switch, except for final state
        """
        for state in states:
            try:
                registers = self.__regs_stateful[state]
            except KeyError:
                continue
            for register in registers:
                register.unregister_item(item)
