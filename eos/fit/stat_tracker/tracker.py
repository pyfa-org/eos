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


import math

from eos.const.eos import State
from eos.const.eve import Attribute
from eos.fit.tuples import DamageTypes, TankingLayers, TankingLayersTotal
from eos.util.volatile_cache import InheritableVolatileMixin, VolatileProperty
from .container import ShipResource, ShipSlots, CharSlots
from .register import (
    DamageDealerRegister, CpuUseRegister, PowerGridUseRegister, CalibrationUseRegister, DroneBayVolumeUseRegister,
    DroneBandwidthUseRegister, TurretUseRegister, LauncherUseRegister, LaunchedDroneRegister
)


class StatTracker(InheritableVolatileMixin):
    """
    Object which is used as access points for all
    fit statistics.

    Required arguments:
    fit -- Fit object to which tracker is assigned
    """

    def __init__(self, fit):
        self._fit = fit
        # Initialize registers
        cpu_reg = CpuUseRegister(fit)
        powergrid_reg = PowerGridUseRegister(fit)
        calibration_reg = CalibrationUseRegister(fit)
        dronebay_reg = DroneBayVolumeUseRegister(fit)
        drone_bandwidth_reg = DroneBandwidthUseRegister(fit)
        turret_reg = TurretUseRegister(fit)
        launcher_reg = LauncherUseRegister(fit)
        launched_drone_reg = LaunchedDroneRegister(fit)
        self._dd_reg = DamageDealerRegister()
        # Dictionary which keeps all stats registers
        # Format: {triggering state: {registers}}
        self.__registers = {
            State.offline: (
                calibration_reg,
                dronebay_reg,
                turret_reg,
                launcher_reg,
                self._dd_reg
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
        super().__init__()

    def _enable_states(self, holder, states):
        """
        Handle state switch upwards.

        Required arguments:
        holder -- holder, for which states are switched
        states -- iterable with states, which are passed
        during state switch, except for initial state
        """
        for state in states:
            # Not all states have corresponding registers,
            # just skip those which don't
            try:
                registers = self.__registers[state]
            except KeyError:
                continue
            for register in registers:
                register.register_holder(holder)

    def _disable_states(self, holder, states):
        """
        Handle state switch downwards.

        Required arguments:
        holder -- holder, for which states are switched
        states -- iterable with states, which are passed
        during state switch, except for final state
        """
        for state in states:
            try:
                registers = self.__registers[state]
            except KeyError:
                continue
            for register in registers:
                register.unregister_holder(holder)

    def _clear_volatile_attrs(self):
        """
        Clear volatile cache for self and all child objects.
        """
        for container in self._volatile_containers:
            container._clear_volatile_attrs()
        InheritableVolatileMixin._clear_volatile_attrs(self)

    @VolatileProperty
    def hp(self):
        """
        Fetch current ship HP and return object with hull, armor, shield and
        total attributes. If fit has no ship or some data cannot be fetched,
        corresponding attribs will be set to None.
        """
        ship_holder = self._fit.ship
        try:
            hp_data = ship_holder.hp
        except AttributeError:
            return TankingLayersTotal(hull=None, armor=None, shield=None, total=None)
        else:
            # Build tuple here because the object we fetched
            # from ship is access point to stats, which are
            # updated on fit changes
            return TankingLayersTotal(
                hull=hp_data.hull,
                armor=hp_data.armor,
                shield=hp_data.shield,
                total=hp_data.total
            )

    @VolatileProperty
    def resistances(self):
        """
        Fetch current ship resistances and return object wit following data:
        .hull.em, .hull.thermal, .hull.kinetic, .hull.explosive,
        .armor.em, .armor.thermal, .armor.kinetic, .armor.explosive,
        .shield.em, .shield.thermal, .shield.kinetic, .shield.explosive
        If fit has no ship or some data cannot be fetched, corresponding attribs
        will be set to None.
        """
        ship_holder = self._fit.ship
        try:
            return ship_holder.resistances
        except AttributeError:
            empty = DamageTypes(em=None, thermal=None, kinetic=None, explosive=None)
            return TankingLayers(hull=empty, armor=empty, shield=empty)

    def get_ehp(self, damage_profile):
        """
        Same as hp, but takes damage_profile argument which defines damage
        profile (should have em, thermal, kinetic and explosive arguments defined
        as numbers). Returns effective HP of a ship against this profile.
        If fit has no ship or some data cannot be fetched, corresponding attribs
        will be set to None.
        """
        ship_holder = self._fit.ship
        try:
            return ship_holder.get_ehp(damage_profile)
        except AttributeError:
            return TankingLayersTotal(hull=None, armor=None, shield=None, total=None)

    @VolatileProperty
    def worst_case_ehp(self):
        """
        Eve-style EHP for a ship - calculated using worst resistance for each layer.
        If fit has no ship or some data cannot be fetched, corresponding attribs
        will be set to None.
        """
        ship_holder = self._fit.ship
        try:
            return ship_holder.worst_case_ehp
        except AttributeError:
            return TankingLayersTotal(hull=None, armor=None, shield=None, total=None)

    def get_nominal_volley(self, holder_filter=None, target_resistances=None):
        """
        Get nominal volley of whole fit.

        Optional arguments:
        holder_filter -- when iterating over fit holder, this function is called.
        If evaluated as True, this holder is taken into consideration, else not.
        If argument is None, all holders 'pass filter'. By default None.
        target_resistances -- resistance profile to calculate effective volley.
        Profile should contain em, thermal, kinetic and explosive attributes as
        numbers in range [0..1]. If None, 'raw' dps is calculated. By default None.

        Return value:
        Object with em, thermal, kinetic, explosive and total attributes.
        """
        volley = self._dd_reg._collect_damage_stats(
            holder_filter,
            'get_nominal_volley',
            target_resistances=target_resistances
        )
        return volley

    def get_nominal_dps(self, holder_filter=None, target_resistances=None, reload=False):
        """
        Get nominal dps of whole fit.

        Optional arguments:
        holder_filter -- when iterating over fit holder, this function is called.
        If evaluated as True, this holder is taken into consideration, else not.
        If argument is None, all holders 'pass filter'. By default None.
        target_resistances -- resistance profile to calculate effective dps.
        Profile should contain em, thermal, kinetic and explosive attributes as
        numbers in range [0..1]. If None, 'raw' dps is calculated. By default None.
        reload -- boolean flag, should reload be taken into consideration or not.
        By default False.

        Return value:
        Object with em, thermal, kinetic, explosive and total attributes.
        """
        dps = self._dd_reg._collect_damage_stats(
            holder_filter,
            'get_nominal_dps',
            target_resistances=target_resistances,
            reload=reload
        )
        return dps

    @VolatileProperty
    def agility_factor(self):
        ship_holder = self._fit.ship
        try:
            ship_attribs = ship_holder.attributes
        except AttributeError:
            return None
        try:
            agility = ship_attribs[Attribute.agility]
            mass = ship_attribs[Attribute.mass]
        except KeyError:
            return None
        real_agility = -math.log(0.25) * agility * mass / 1000000
        return real_agility

    @VolatileProperty
    def align_time(self):
        try:
            return math.ceil(self.agility_factor)
        except TypeError:
            return None
