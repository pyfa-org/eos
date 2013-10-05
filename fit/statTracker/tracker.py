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
        cpuReg = CpuUseRegister(fit)
        pgReg = PowerGridUseRegister(fit)
        calibReg = CalibrationUseRegister(fit)
        droneBayReg = DroneBayVolumeUseRegister(fit)
        droneBwReg = DroneBandwidthUseRegister(fit)
        turretReg = TurretUseRegister(fit)
        launcherReg = LauncherUseRegister(fit)
        launchedDroneReg = LaunchedDroneRegister(fit)
        # Dictionary which keeps all stats registers
        # Format: {triggering state: {registers}}
        self.__registers = {State.offline: (calibReg,
                                            droneBayReg,
                                            turretReg,
                                            launcherReg),
                            State.online:  (cpuReg,
                                            pgReg,
                                            droneBwReg,
                                            launchedDroneReg)}
        # Initialize sub-containers
        self.cpu = ShipResource(fit, cpuReg, Attribute.cpuOutput)
        self.powerGrid = ShipResource(fit, pgReg, Attribute.powerOutput)
        self.calibration = ShipResource(fit, calibReg, Attribute.upgradeCapacity)
        self.droneBay = ShipResource(fit, droneBayReg, Attribute.droneCapacity)
        self.droneBandwidth = ShipResource(fit, droneBwReg, Attribute.droneBandwidth)
        self.highSlots = ShipSlots(fit, fit.modules.high, Attribute.hiSlots)
        self.medSlots = ShipSlots(fit, fit.modules.med, Attribute.medSlots)
        self.lowSlots = ShipSlots(fit, fit.modules.low, Attribute.lowSlots)
        self.rigSlots = ShipSlots(fit, fit.rigs, Attribute.rigSlots)
        self.subsystemSlots = ShipSlots(fit, fit.subsystems, Attribute.subSystemSlot)
        self.turretSlots = ShipSlots(fit, turretReg, Attribute.turretSlotsLeft)
        self.launcherSlots = ShipSlots(fit, launcherReg, Attribute.launcherSlotsLeft)
        self.launchedDrones = CharSlots(fit, launchedDroneReg, Attribute.maxActiveDrones)

    def _enableStates(self, holder, states):
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
                register.registerHolder(holder)

    def _disableStates(self, holder, states):
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
                register.unregisterHolder(holder)

    @property
    def agilityFactor(self):
        try:
            shipAttribs = self._fit.ship.attributes
        except AttributeError:
            return None
        try:
            agility = shipAttribs[Attribute.agility]
            mass = shipAttribs[Attribute.mass]
        except KeyError:
            return None
        realAgility = -math.log(0.25) * agility * mass / 1000000
        return realAgility

    @property
    def alignTime(self):
        try:
            return math.ceil(self.agilityFactor)
        except TypeError:
            return None
