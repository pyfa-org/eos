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


from eos.const.eos import State
from eos.fit.messages import HolderStateChanged
from eos.util.pubsub import BaseSubscriber
from .exception import RegisterValidationError, ValidationError
from .register import *


class RestrictionTracker(BaseSubscriber):
    """
    Track all restrictions applied to fitting and expose functionality
    to validate against various criteria. Actually works as middle-layer
    between fit and restriction registers, managing them and providing
    results to fit.

    Required arguments:
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
        self.__registers = {
            State.offline: (
                CalibrationRegister(fit),
                DroneBayVolumeRegister(fit),
                HolderClassRegister(),
                HighSlotRegister(fit),
                MediumSlotRegister(fit),
                LowSlotRegister(fit),
                RigSlotRegister(fit),
                SubsystemSlotRegister(fit),
                TurretSlotRegister(fit),
                LauncherSlotRegister(fit),
                SubsystemIndexRegister(),
                ImplantIndexRegister(),
                BoosterIndexRegister(),
                ShipTypeGroupRegister(fit),
                CapitalItemRegister(fit),
                MaxGroupFittedRegister(),
                DroneGroupRegister(fit),
                RigSizeRegister(fit),
                SkillRequirementRegister(fit),
                ChargeGroupRegister(),
                ChargeSizeRegister(),
                ChargeVolumeRegister(),
                BoosterEffectRegister()
            ),
            State.online: (
                CpuRegister(fit),
                PowerGridRegister(fit),
                DroneBandwidthRegister(fit),
                MaxGroupOnlineRegister(),
                LaunchedDroneRegister(fit),
                StateRegister()
            ),
            State.active: (
                MaxGroupActiveRegister(),
            )
        }
        fit._subscribe(self, (HolderStateChanged,))

    def validate(self, skip_checks):
        """
        Validate fit.

        Optional arguments:
        skip_checks -- iterable with restriction types, for which
        checks are skipped

        Possible exceptions:
        ValidationError -- if any failure is occurred during
        validation, this exception is thrown, with all failure
        data in its arguments.
        """
        # Container for validation error data
        # Format: {holder: {error type: error data}}
        invalid_holders = {}
        # Go through all known registers
        for state in self.__registers:
            for register in self.__registers[state]:
                # Skip check if we're told to do so, based
                # on exception class assigned to register
                restriction_type = register.restriction_type
                if restriction_type in skip_checks:
                    continue
                # Run validation for current register, if validation
                # failure exception is raised - add it to container
                try:
                    register.validate()
                except RegisterValidationError as e:
                    # All erroneous holders should be in 1st argument
                    # of raised exception
                    exception_data = e.args[0]
                    for holder in exception_data:
                        holder_error = exception_data[holder]
                        # Fill container for invalid holders
                        holder_errors = invalid_holders.setdefault(holder, {})
                        holder_errors[restriction_type] = holder_error
        # Raise validation error only if we got any
        # failures
        if invalid_holders:
            raise ValidationError(invalid_holders)

    def _handle_holder_state_change(self, message):
        """
        Handle state switch.

        Required arguments:
        holder -- holder, for which state is switched
        message -- message with relevant information
        """
        holder, old_state, new_state = message
        min_state = min(old_state, new_state)
        max_state = max(old_state, new_state)
        states = set(filter(lambda s: min_state < s <= max_state, State))
        for state in states:
            # Not all states have corresponding registers,
            # just skip those which don't
            try:
                registers = self.__registers[state]
            except KeyError:
                continue
            for register in registers:
                if new_state > old_state:
                    register.register_holder(holder)
                else:
                    register.unregister_holder(holder)

    _handler_map = {
        HolderStateChanged: _handle_holder_state_change
    }

    def _notify(self, message):
        try:
            handler = self._handler_map[type(message)]
        except KeyError:
            return
        handler(self, message)

    def enable_states(self, holder, states):
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

    def disable_states(self, holder, states):
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
