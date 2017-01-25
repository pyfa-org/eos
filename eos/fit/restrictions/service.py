# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2017 Anton Vorobyov
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


from itertools import chain

from eos.const.eos import State
from eos.fit.messages import HolderAdded, HolderRemoved, HolderStateChanged, EnableServices, DisableServices
from eos.util.pubsub import BaseSubscriber
from .exception import RegisterValidationError, ValidationError
from .register import *


class RestrictionService(BaseSubscriber):
    """
    Track all restrictions applied to fitting and expose functionality
    to validate against various criteria. Actually works as middle-layer
    between fit and restriction registers, managing them and providing
    results to fit.

    Required arguments:
    fit -- Fit object to which service is assigned
    """

    def __init__(self, fit):
        self.__enabled = False
        # Fit reference, to which this restriction service
        # is attached
        self._fit = fit
        # Set with 'stateless' holders. Holders are always
        # tracked by these, regardless of state
        # Format: (registers,)
        self.__regs_stateless = (
            CalibrationRegister(fit),
            DroneBayVolumeRegister(fit),
            HolderClassRestrictionRegister(),
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
            ShipTypeGroupRestrictionRegister(fit),
            CapitalItemRestrictionRegister(fit),
            MaxGroupFittedRegister(),
            DroneGroupRestrictionRegister(fit),
            RigSizeRestrictionRegister(fit),
            SkillRequirementRestrictionRegister(fit),
            ChargeGroupRestrictionRegister(),
            ChargeSizeRestrictionRegister(),
            ChargeVolumeRestrictionRegister(),
            BoosterEffectRestrictionRegister()
        )
        # Dictionary with 'stateful' registers. When holders
        # is in corresponding state or above, register tracks
        # such holder and may raise restriction violations
        # Format: {triggering state: {registers}}
        self.__regs_stateful = {
            State.offline: (
                StateRestrictionRegister(),
            ),
            State.online: (
                CpuRegister(fit),
                PowerGridRegister(fit),
                DroneBandwidthRegister(fit),
                MaxGroupOnlineRegister(),
                LaunchedDroneRegister(fit)
            ),
            State.active: (
                MaxGroupActiveRegister(),
            )
        }
        fit._subscribe(self, self._handler_map.keys())

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
        for register in chain(self.__regs_stateless, *self.__regs_stateful.values()):
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

    # Message handling
    def _handle_holder_addition(self, message):
        if not self.__enabled:
            return
        self.__add_holder(message.holder)

    def _handle_holder_removal(self, message):
        if not self.__enabled:
            return
        self.__remove_holder(message.holder)

    def _handle_holder_state_change(self, message):
        if not self.__enabled:
            return
        holder, old_state, new_state = message
        if new_state > old_state:
            states = set(filter(lambda s: old_state < s <= new_state, State))
            self.__enable_states(holder, states)
        elif new_state < old_state:
            states = set(filter(lambda s: new_state < s <= old_state, State))
            self.__disable_states(holder, states)

    def _handle_enable_services(self, message):
        """
        Enable service and register passed holders.
        """
        self.__enabled = True
        for holder in message.holders:
            self.__add_holder(holder)

    def _handle_disable_services(self, message):
        """
        Unregister passed holders from this service and
        disable it.
        """
        for holder in message.holders:
            self.__remove_holder(holder)
        self.__enabled = False

    _handler_map = {
        HolderAdded: _handle_holder_addition,
        HolderRemoved: _handle_holder_removal,
        HolderStateChanged: _handle_holder_state_change,
        EnableServices: _handle_enable_services,
        DisableServices: _handle_disable_services
    }

    def _notify(self, message):
        try:
            handler = self._handler_map[type(message)]
        except KeyError:
            return
        handler(self, message)

    # Private methods for message handlers
    def __add_holder(self, holder):
        for register in self.__regs_stateless:
            register.register_item(holder)
        states = set(filter(lambda s: s <= holder.state, State))
        self.__enable_states(holder, states)

    def __remove_holder(self, holder):
        states = set(filter(lambda s: s <= holder.state, State))
        self.__disable_states(holder, states)
        for register in self.__regs_stateless:
            register.unregister_item(holder)

    def __enable_states(self, holder, states):
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
                registers = self.__regs_stateful[state]
            except KeyError:
                continue
            for register in registers:
                register.register_item(holder)

    def __disable_states(self, holder, states):
        """
        Handle state switch downwards.

        Required arguments:
        holder -- holder, for which states are switched
        states -- iterable with states, which are passed
        during state switch, except for final state
        """
        for state in states:
            try:
                registers = self.__regs_stateful[state]
            except KeyError:
                continue
            for register in registers:
                register.unregister_item(holder)
