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
from .stat import *


class StatsTracker:

    def __init__(self, fit):
        self._fit = fit
        self.__cpuStats = CpuRegister(fit)
        # Dictionary which keeps all stats registers
        # Format: {triggering state: {registers}}
        self.__registers = {State.offline: (),
                            State.online:  (self.__cpuStats,),
                            State.active:  ()}

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
    def cpu(self):
        return self.__cpuStats.getResourceStats()

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
