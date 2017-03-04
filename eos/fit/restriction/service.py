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
from eos.fit.pubsub.message import InstrItemAdd, InstrItemRemove, InstrStatesActivate, InstrStatesDeactivate
from eos.fit.pubsub.subscriber import BaseSubscriber
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
        # Set of restrictions which do not need
        # item registration
        self.__rests = (
            BoosterEffectRestriction(fit),
            DroneGroupRestriction(fit),
            HighSlotRestriction(fit),
            ItemClassRestrictionRegister(),
            LowSlotRestriction(fit),
            MediumSlotRestriction(fit),
            RigSlotRestriction(fit),
            StateRestrictionRegister(),
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
                    invalid_items.setdefault(item, {})[restriction_type] = item_error
        # Raise validation error only if we got any
        # failures
        if invalid_items:
            raise ValidationError(invalid_items)

    # Message handling
    def _handle_item_addition(self, message):
        for register in self.__rest_regs_stateless:
            register.register_item(message.item)

    def _handle_item_removal(self, message):
        for register in self.__rest_regs_stateless:
            register.unregister_item(message.item)

    def _handle_item_states_activate(self, message):
        for state in message.states:
            # Not all states have corresponding registers,
            # just skip those which don't
            try:
                registers = self.__rest_regs_stateful[state]
            except KeyError:
                continue
            for register in registers:
                register.register_item(message.item)

    def _handle_item_states_deactivate(self, message):
        for state in message.states:
            try:
                registers = self.__rest_regs_stateful[state]
            except KeyError:
                continue
            for register in registers:
                register.unregister_item(message.item)

    _handler_map = {
        InstrItemAdd: _handle_item_addition,
        InstrItemRemove: _handle_item_removal,
        InstrStatesActivate: _handle_item_states_activate,
        InstrStatesDeactivate: _handle_item_states_deactivate
    }

    def _notify(self, message):
        try:
            handler = self._handler_map[type(message)]
        except KeyError:
            return
        handler(self, message)
