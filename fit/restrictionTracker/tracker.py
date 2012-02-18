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
from .register.resource import CpuRegister
from .register.slotNumber import HighSlotRegister
from .register.shipTypeGroup import ShipTypeGroupRegister
from .register.maxGroup import MaxGroupFittedRegister
from .register.capitalItem import CapitalItemRegister
from .register.slotIndex import ImplantSlotIndexRegister


class RestrictionTracker:
    def __init__(self, fit):
        self.__fit = fit
        self.__cpuRegister = CpuRegister(fit)
        self.__highSlotRegister = HighSlotRegister(fit)
        self.__maxGroupFittedRegister = MaxGroupFittedRegister()
        self.__shipTypeGroupRegister = ShipTypeGroupRegister(fit)
        self.__capitalItemRegister = CapitalItemRegister(fit)
        self.__implantSlotIndexRegister = ImplantSlotIndexRegister()

    def addHolder(self, holder):
        self.__highSlotRegister.registerHolder(holder)
        self.__maxGroupFittedRegister.registerHolder(holder)
        self.__shipTypeGroupRegister.registerHolder(holder)
        self.__capitalItemRegister.registerHolder(holder)
        self.__implantSlotIndexRegister.registerHolder(holder)

    def removeHolder(self, holder):
        self.__highSlotRegister.unregisterHolder(holder)
        self.__maxGroupFittedRegister.unregisterHolder(holder)
        self.__shipTypeGroupRegister.unregisterHolder(holder)
        self.__capitalItemRegister.unregisterHolder(holder)
        self.__implantSlotIndexRegister.unregisterHolder(holder)

    def stateSwitch(self, holder, oldState, newState):
        if (oldState is None or oldState < State.online) and (newState is not None and newState >= State.online):
            self.__cpuRegister.registerHolder(holder)
        elif (newState is None or newState < State.online) and (oldState is not None and oldState >= State.online):
            self.__cpuRegister.unregisterHolder(holder)

    def validate(self):
        self.__cpuRegister.validate()
        self.__highSlotRegister.validate()
        self.__maxGroupFittedRegister.validate()
        self.__shipTypeGroupRegister.validate()
        self.__capitalItemRegister.validate()
        self.__implantSlotIndexRegister.validate()
