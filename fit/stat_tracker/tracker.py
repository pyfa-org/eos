#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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
#===============================================================================


import math

from eos.const.eos import State
from eos.const.eve import Attribute
from eos.fit.tuples import DamageTypes, Hitpoints, TankingLayers
from .container import *
from .register import *


class StatTracker:
    """
    Object which is used as access points for all
    fit statistics.

    Positional arguments:
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
        # Dictionary which keeps all stats registers
        # Format: {triggering state: {registers}}
        self.__registers = {
            State.offline: (
                calibration_reg,
                dronebay_reg,
                turret_reg,
                launcher_reg
            ),
            State.online:  (
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

    def _enable_states(self, holder, states):
        """
        Handle state switch upwards.

        Positional arguments:
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

        Positional arguments:
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

    @property
    def hp(self):
        ship_holder = self._fit.ship
        try:
            return ship_holder.hp
        except AttributeError:
            return Hitpoints(hull=None, armor=None, shield=None, total=0)

    @property
    def resistances(self):
        ship_holder = self._fit.ship
        try:
            return ship_holder.resistances
        except AttributeError:
            empty = DamageTypes(em=None, thermal=None, kinetic=None, explosive=None)
            return TankingLayers(hull=empty, armor=empty, shield=empty)

    def get_ehp(self, damage_profile):
        ship_holder = self._fit.ship
        try:
            return ship_holder.get_ehp(damage_profile)
        except AttributeError:
            return Hitpoints(hull=None, armor=None, shield=None, total=0)

    @property
    def worst_case_ehp(self):
        ship_holder = self._fit.ship
        try:
            return ship_holder.worst_case_ehp
        except AttributeError:
            return Hitpoints(hull=None, armor=None, shield=None, total=0)

    @property
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

    @property
    def align_time(self):
        try:
            return math.ceil(self.agility_factor)
        except TypeError:
            return None
