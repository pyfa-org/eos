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
from .restriction.capitalItem import CapitalItemRegister
from .restriction.droneGroup import DroneGroupRegister
from .restriction.droneNumber import DroneNumberRegister
from .restriction.maxGroup import MaxGroupFittedRegister, MaxGroupOnlineRegister, MaxGroupActiveRegister
from .restriction.resource import CpuRegister, PowerGridRegister, CalibrationRegister, DroneBayVolumeRegister, \
DroneBandwidthRegister
from .restriction.rigSize import RigSizeRegister
from .restriction.shipTypeGroup import ShipTypeGroupRegister
from .restriction.skillRequirement import SkillRequirementRegister
from .restriction.slotIndex import SubsystemIndexRegister, ImplantIndexRegister, BoosterIndexRegister
from .restriction.slotNumber import HighSlotRegister, MediumSlotRegister, LowSlotRegister, RigSlotRegister, \
SubsystemSlotRegister, TurretSlotRegister, LauncherSlotRegister


class RestrictionTracker:
    def __init__(self, fit):
        # Fit reference, to which this restriction tracker
        # is attached
        self._fit = fit
        # Dictionary which keeps all restriction registers
        # used by tracker. When some holder passes state stored
        # as key, it's registered/unregistered in registers
        # stored as value. None state means that holders are
        # registered/unregistered when they're added/removed
        # to fit, not when they enter or leave some state
        # Format: {triggering state: {registers}}
        self.__registers = {State.offline: {CalibrationRegister(self),
                                            DroneBayVolumeRegister(self),
                                            HighSlotRegister(self),
                                            MediumSlotRegister(self),
                                            LowSlotRegister(self),
                                            RigSlotRegister(self),
                                            SubsystemSlotRegister(self),
                                            TurretSlotRegister(self),
                                            LauncherSlotRegister(self),
                                            SubsystemIndexRegister(),
                                            ImplantIndexRegister(),
                                            BoosterIndexRegister(),
                                            ShipTypeGroupRegister(self),
                                            CapitalItemRegister(self),
                                            MaxGroupFittedRegister(),
                                            DroneGroupRegister(self),
                                            RigSizeRegister(self),
                                            SkillRequirementRegister()},
                            State.online:  {CpuRegister(self),
                                            PowerGridRegister(self),
                                            DroneBandwidthRegister(self),
                                            MaxGroupOnlineRegister(),
                                            DroneNumberRegister(self)},
                            State.active:  {MaxGroupActiveRegister()}}

    def enableStates(self, holder, states):
        for state in states:
            try:
                registers = self.__registers[state]
            except KeyError:
                continue
            for register in registers:
                register.registerHolder(holder)

    def disableStates(self, holder, states):
        for state in states:
            try:
                registers = self.__registers[state]
            except KeyError:
                continue
            for register in registers:
                register.unregisterHolder(holder)

    def validate(self):
        for state in self.__registers:
            for register in self.__registers[state]:
                register.validate()
