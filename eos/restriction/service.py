# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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
# ==============================================================================


from .exception import RestrictionValidationError
from .exception import ValidationError
from .restriction import BoosterIndexRestrictionRegister
from .restriction import CalibrationRestriction
from .restriction import CapitalItemRestrictionRegister
from .restriction import ChargeGroupRestrictionRegister
from .restriction import ChargeSizeRestrictionRegister
from .restriction import ChargeVolumeRestrictionRegister
from .restriction import CpuRestriction
from .restriction import DroneBandwidthRestriction
from .restriction import DroneBayVolumeRestriction
from .restriction import DroneGroupRestrictionRegister
from .restriction import FighterSquadHeavyRestriction
from .restriction import FighterSquadLightRestriction
from .restriction import FighterSquadRestriction
from .restriction import FighterSquadSupportRestriction
from .restriction import HighSlotRestriction
from .restriction import ImplantIndexRestrictionRegister
from .restriction import ItemClassRestriction
from .restriction import LaunchedDroneRestriction
from .restriction import LauncherSlotRestriction
from .restriction import LoadedItemRestriction
from .restriction import LowSlotRestriction
from .restriction import MaxGroupActiveRestrictionRegister
from .restriction import MaxGroupFittedRestrictionRegister
from .restriction import MaxGroupOnlineRestrictionRegister
from .restriction import MidSlotRestriction
from .restriction import PowergridRestriction
from .restriction import RigSizeRestrictionRegister
from .restriction import RigSlotRestriction
from .restriction import ShipTypeGroupRestrictionRegister
from .restriction import SkillRequirementRestrictionRegister
from .restriction import StateRestrictionRegister
from .restriction import SubsystemIndexRestrictionRegister
from .restriction import SubsystemSlotRestriction
from .restriction import TurretSlotRestriction


class RestrictionService:
    """
    Track all restrictions applicable to fit.

    Works as middle-layer between fit and restriction registers, managing them
    and providing results to fit.

    Args:
        fit: Fit instance which this service is attached to.
    """

    def __init__(self, fit):
        # Container for all restrictions
        self.__restrictions = {
            BoosterIndexRestrictionRegister(fit),
            CalibrationRestriction(fit),
            CapitalItemRestrictionRegister(fit),
            ChargeGroupRestrictionRegister(fit),
            ChargeSizeRestrictionRegister(fit),
            ChargeVolumeRestrictionRegister(fit),
            CpuRestriction(fit),
            DroneBandwidthRestriction(fit),
            DroneBayVolumeRestriction(fit),
            DroneGroupRestrictionRegister(fit),
            FighterSquadHeavyRestriction(fit),
            FighterSquadLightRestriction(fit),
            FighterSquadRestriction(fit),
            FighterSquadSupportRestriction(fit),
            HighSlotRestriction(fit),
            ImplantIndexRestrictionRegister(fit),
            ItemClassRestriction(fit),
            LaunchedDroneRestriction(fit),
            LauncherSlotRestriction(fit),
            LoadedItemRestriction(fit),
            LowSlotRestriction(fit),
            MaxGroupActiveRestrictionRegister(fit),
            MaxGroupFittedRestrictionRegister(fit),
            MaxGroupOnlineRestrictionRegister(fit),
            MidSlotRestriction(fit),
            PowergridRestriction(fit),
            RigSizeRestrictionRegister(fit),
            RigSlotRestriction(fit),
            ShipTypeGroupRestrictionRegister(fit),
            SkillRequirementRestrictionRegister(fit),
            StateRestrictionRegister(fit),
            SubsystemIndexRestrictionRegister(fit),
            SubsystemSlotRestriction(fit),
            TurretSlotRestriction(fit)}

    def validate(self, skip_checks=()):
        """Validate fit.

        Args:
            skip_checks (optional): Iterable with restriction types validation
                should ignore. By default, nothing is ignored.

        Raises:
            ValidationError: If fit validation fails. Its single argument
                contains extensive data on reason of failure. Refer to
                restriction service docs for format of the data.
        """
        # Container for validation error data
        # Format: {item: {error type: error data}}
        invalid_items = {}
        # Go through all known registers
        for restriction in self.__restrictions:
            # Skip check if we're told to do so, based on restriction class
            # assigned to the register
            restriction_type = restriction.type
            if restriction_type in skip_checks:
                continue
            # Run validation for current register, if validation failure
            # exception is raised - add it to container
            try:
                restriction.validate()
            except RestrictionValidationError as e:
                # All erroneous items should be in 1st argument of raised
                # exception
                exception_data = e.args[0]
                for item in exception_data:
                    item_error = exception_data[item]
                    item_errors = invalid_items.setdefault(item, {})
                    item_errors[restriction_type] = item_error
        # Raise validation error only if we got any failures
        if invalid_items:
            raise ValidationError(invalid_items)
