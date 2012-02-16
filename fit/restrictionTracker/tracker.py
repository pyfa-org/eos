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
from .register.highSlot import HighSlotRegister
from .register.groupFitted import GroupFittedRegister
from .register.shipItemSize import ShipItemSizeRegister
from .exception import CpuException, HighSlotException, GroupFittedException, ShipItemSizeException


class RestrictionTracker:
    def __init__(self, fit):
        self.__fit = fit
        self.__cpuRegister = CpuRegister(fit)
        self.__highSlotRegister = HighSlotRegister(fit)
        self.__groupFittedRegister = GroupFittedRegister()
        self.__shipItemSizeRegister = ShipItemSizeRegister(fit)

    def addHolder(self, holder):
        try:
            self.__highSlotRegister.registerHolder(holder)
        except HighSlotException:
            self.__highSlotRegister.unregisterHolder(holder)
            raise
        try:
            self.__groupFittedRegister.registerHolder(holder)
        except GroupFittedException:
            self.__groupFittedRegister.unregisterHolder(holder)
            raise
        try:
            self.__shipItemSizeRegister.registerHolder(holder)
        except ShipItemSizeException:
            self.__shipItemSizeRegister.unregisterHolder(holder)
            raise

    def removeHolder(self, holder):
        self.__highSlotRegister.unregisterHolder(holder)
        self.__groupFittedRegister.unregisterHolder(holder)
        self.__shipItemSizeRegister.unregisterHolder(holder)

    def stateSwitch(self, holder, oldState, newState):
        if (oldState is None or oldState < State.online) and (newState is not None and newState >= State.online):
            try:
                self.__cpuRegister.registerHolder(holder)
            except CpuException:
                self.__cpuRegister.unregisterHolder(holder)
                raise
        elif (newState is None or newState < State.online) and (oldState is not None and oldState >= State.online):
            self.__cpuRegister.unregisterHolder(holder)

    def validate(self):
        self.__cpuRegister.validate()
        self.__highSlotRegister.validate()
        self.__shipItemSizeRegister.validate()
