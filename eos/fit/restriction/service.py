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
from eos.fit.messages import ItemAdded, ItemRemoved, ItemStateChanged, EnableServices, DisableServices
from eos.util.pubsub import BaseSubscriber
from .exception import RegisterValidationError, ValidationError
from .restriction import *


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
        # Set of restrictions which do not need
        # item registration
        self.__rests = (
            BoosterEffectRestriction(fit),
            DroneGroupRestriction(fit),
            HighSlotRestriction(fit),
            ItemClassRestriction(fit),
            LowSlotRestriction(fit),
            MediumSlotRestriction(fit),
            RigSlotRestriction(fit),
            StateRestriction(fit),
            SubsystemSlotRestriction(fit)
        )
        # Set with 'stateless' restriction registers. Items
        # are always tracked by these, regardless of state
        # Format: (registers,)
        self.__rest_regs_stateless = (
            BoosterIndexRegister(),
            CalibrationRegister(fit),
            CapitalItemRestrictionRegister(fit),
            ChargeGroupRestrictionRegister(),
            ChargeSizeRestrictionRegister(),
            ChargeVolumeRestrictionRegister(),
            DroneBayVolumeRegister(fit),
            ImplantIndexRegister(),
            LauncherSlotRestrictionRegister(fit),
            MaxGroupFittedRegister(),
            RigSizeRestrictionRegister(fit),
            ShipTypeGroupRestrictionRegister(fit),
            SkillRequirementRestrictionRegister(fit),
            SubsystemIndexRegister(),
            TurretSlotRestrictionRegister(fit)
        )
        # Dictionary with 'stateful' restriction registers. When
        # item is in corresponding state or above, register tracks
        # such item and may raise restriction violations
        # Format: {triggering state: {registers}}
        self.__rest_regs_stateful = {
            State.online: (
                CpuRegister(fit),
                DroneBandwidthRegister(fit),
                LaunchedDroneRestrictionRegister(fit),
                MaxGroupOnlineRegister(),
                PowerGridRegister(fit)
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
        if self.__enabled is not True:
            return
        # Container for validation error data
        # Format: {item: {error type: error data}}
        invalid_items = {}
        # Go through all known registers
        for register in chain(
            self.__rests, self.__rest_regs_stateless,
            *self.__rest_regs_stateful.values()
        ):
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
                # All erroneous items should be in 1st argument
                # of raised exception
                exception_data = e.args[0]
                for item in exception_data:
                    item_error = exception_data[item]
                    # Fill container for invalid items
                    item_errors = invalid_items.setdefault(item, {})
                    item_errors[restriction_type] = item_error
        # Raise validation error only if we got any
        # failures
        if invalid_items:
            raise ValidationError(invalid_items)

    # Message handling
    def _handle_item_addition(self, message):
        if not self.__enabled:
            return
        self.__add_item(message.item)

    def _handle_item_removal(self, message):
        if not self.__enabled:
            return
        self.__remove_item(message.item)

    def _handle_item_state_change(self, message):
        if not self.__enabled:
            return
        item, old_state, new_state = message
        if new_state > old_state:
            states = set(filter(lambda s: old_state < s <= new_state, State))
            self.__enable_states(item, states)
        elif new_state < old_state:
            states = set(filter(lambda s: new_state < s <= old_state, State))
            self.__disable_states(item, states)

    def _handle_enable_services(self, message):
        """
        Enable service and register passed items.
        """
        self.__enabled = True
        for item in message.items:
            self.__add_item(item)

    def _handle_disable_services(self, message):
        """
        Unregister passed items from this service and
        disable it.
        """
        for item in message.items:
            self.__remove_item(item)
        self.__enabled = False

    _handler_map = {
        ItemAdded: _handle_item_addition,
        ItemRemoved: _handle_item_removal,
        ItemStateChanged: _handle_item_state_change,
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
    def __add_item(self, item):
        for register in self.__rest_regs_stateless:
            register.register_item(item)
        states = set(filter(lambda s: s <= item.state, State))
        self.__enable_states(item, states)

    def __remove_item(self, item):
        states = set(filter(lambda s: s <= item.state, State))
        self.__disable_states(item, states)
        for register in self.__rest_regs_stateless:
            register.unregister_item(item)

    def __enable_states(self, item, states):
        """
        Handle state switch upwards.

        Required arguments:
        item -- item, for which states are switched
        states -- iterable with states, which are passed
        during state switch, except for initial state
        """
        for state in states:
            # Not all states have corresponding registers,
            # just skip those which don't
            try:
                registers = self.__rest_regs_stateful[state]
            except KeyError:
                continue
            for register in registers:
                register.register_item(item)

    def __disable_states(self, item, states):
        """
        Handle state switch downwards.

        Required arguments:
        item -- item, for which states are switched
        states -- iterable with states, which are passed
        during state switch, except for final state
        """
        for state in states:
            try:
                registers = self.__rest_regs_stateful[state]
            except KeyError:
                continue
            for register in registers:
                register.unregister_item(item)
