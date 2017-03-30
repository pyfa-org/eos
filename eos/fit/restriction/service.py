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


from .exception import RestrictionValidationError, ValidationError
from .restriction import *


class RestrictionService:
    """
    Track all restrictions applied to fitting and expose functionality
    to validate against various criteria. Actually works as middle-layer
    between fit and restriction registers, managing them and providing
    results to fit.

    Required arguments:
    fit -- Fit object to which service is assigned
    """

    def __init__(self, fit):
        # Container for all restrictions
        self.__restrictions = {
            BoosterEffectRestriction(fit),
            BoosterIndexRestriction(fit),
            CalibrationRestriction(fit),
            CapitalItemRestriction(fit),
            ChargeGroupRestriction(fit),
            ChargeSizeRestriction(fit),
            ChargeVolumeRestriction(fit),
            CpuRestriction(fit),
            DroneBandwidthRestriction(fit),
            DroneBayVolumeRestriction(fit),
            DroneGroupRestriction(fit),
            HighSlotRestriction(fit),
            ImplantIndexRestriction(fit),
            ItemClassRestriction(fit),
            LaunchedDroneRestriction(fit),
            LauncherSlotRestriction(fit),
            LowSlotRestriction(fit),
            MaxGroupActiveRestriction(fit),
            MaxGroupFittedRestriction(fit),
            MaxGroupOnlineRestriction(fit),
            MediumSlotRestriction(fit),
            PowerGridRestriction(fit),
            RigSizeRestriction(fit),
            RigSlotRestriction(fit),
            ShipTypeGroupRestriction(fit),
            SkillRequirementRestriction(fit),
            StateRestriction(fit),
            SubsystemIndexRestriction(fit),
            SubsystemSlotRestriction(fit),
            TurretSlotRestriction(fit)
        }

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
        for restriction in self.__restrictions:
            # Skip check if we're told to do so, based
            # on exception class assigned to register
            restriction_type = restriction.type
            if restriction_type in skip_checks:
                continue
            # Run validation for current register, if validation
            # failure exception is raised - add it to container
            try:
                restriction.validate()
            except RestrictionValidationError as e:
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
