#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2012 Anton Vorobyov
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


from eos.const import State
from .register.cpu import CpuRegister
from .register.slotNumber import HighSlotRegister
from .register.shipGroup import ShipGroupRegister
from .register.maxGroup import MaxGroupFittedRegister
from .register.capitalModule import CapitalModuleRegister


class RestrictionTracker:
    def __init__(self, fit):
        self.__fit = fit
        self.__cpuRegister = CpuRegister(fit)
        self.__highSlotRegister = HighSlotRegister(fit)
        self.__maxGroupFittedRegister = MaxGroupFittedRegister()
        self.__shipGroupRegister = ShipGroupRegister(fit)
        self.__capitalModuleRegister = CapitalModuleRegister(fit)

    def addHolder(self, holder):
        self.__highSlotRegister.registerHolder(holder)
        self.__maxGroupFittedRegister.registerHolder(holder)
        self.__shipGroupRegister.registerHolder(holder)
        self.__capitalModuleRegister.registerHolder(holder)

    def removeHolder(self, holder):
        self.__highSlotRegister.unregisterHolder(holder)
        self.__maxGroupFittedRegister.unregisterHolder(holder)
        self.__shipGroupRegister.unregisterHolder(holder)
        self.__capitalModuleRegister.unregisterHolder(holder)

    def stateSwitch(self, holder, oldState, newState):
        if (oldState is None or oldState < State.online) and (newState is not None and newState >= State.online):
            self.__cpuRegister.registerHolder(holder)
        elif (newState is None or newState < State.online) and (oldState is not None and oldState >= State.online):
            self.__cpuRegister.unregisterHolder(holder)

    def validate(self):
        self.__cpuRegister.validate()
        self.__highSlotRegister.validate()
        self.__maxGroupFittedRegister.validate()
        self.__shipGroupRegister.validate()
        self.__capitalModuleRegister.validate()
