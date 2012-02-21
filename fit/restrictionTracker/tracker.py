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
from .exception import RegisterValidationError, ValidationError
from .restriction.capitalItem import CapitalItemRegister
from .restriction.droneGroup import DroneGroupRegister
from .restriction.launchedDrone import LaunchedDroneRegister
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
    """
    Track all restrictions applied to fitting and expose functionality
    to validate against various criteria. Actually works as middle-layer
    between fit and restriction registers, managing them and providing
    results to fit.

    Positional arguments:
    fit -- Fit object to which tracker is assigned
    """

    def __init__(self, fit):
        # Fit reference, to which this restriction tracker
        # is attached
        self._fit = fit
        # Dictionary which keeps all restriction registers
        # used by tracker. When some holder passes state stored
        # as key, it's registered/unregistered in registers
        # stored as value.
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
                                            LaunchedDroneRegister(self)},
                            State.active:  {MaxGroupActiveRegister()}}

    def enableStates(self, holder, states):
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

    def disableStates(self, holder, states):
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

    def validate(self, skipChecks=set()):
        """
        Validate fit.

        Keyword arguments:
        skipChecks -- iterable with restriction types, for which
        checks are skipped (default is empty set)

        Possible exceptions:
        ValidationError -- if any failure is occurred during
        validation, this exception is thrown, with all failure
        data in its arguments.
        """
        # Container for validation error data
        # Format: {holder: {error type: error data}}
        invalidHolders = {}
        # Go through all known registers
        for state in self.__registers:
            for register in self.__registers[state]:
                # Skip check if we're told to do so, based
                # on exception class assigned to register
                restrictionType = register.restrictionType
                if restrictionType in skipChecks:
                    continue
                # Run validation for current register, if validation
                # failure exception is raised - add it to container
                try:
                    register.validate()
                except RegisterValidationError as e:
                    # All erroneous holders should be in 1st argument
                    # of raised exception
                    exceptionData = e.args[0]
                    for holder in exceptionData:
                        holderError = exceptionData[holder]
                        # Fill container for invalid holders
                        try:
                            holderErrors = invalidHolders[holder]
                        except KeyError:
                            holderErrors = invalidHolders[holder] = {}
                        holderErrors[restrictionType] = holderError
        # Raise validation error only if we got any
        # failures
        if len(invalidHolders) > 0:
            raise ValidationError(invalidHolders)
