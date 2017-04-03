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


__all__ = [
    'BoosterEffectRestrictionRegister',
    'BoosterIndexRestriction',
    'CalibrationRestriction',
    'CapitalItemRestriction',
    'CpuRestriction',
    'ChargeGroupRestriction',
    'ChargeSizeRestriction',
    'ChargeVolumeRestriction',
    'DroneBandwidthRestriction',
    'DroneBayVolumeRestriction',
    'DroneGroupRestriction',
    'HighSlotRestriction',
    'ImplantIndexRestriction',
    'ItemClassRestriction',
    'LaunchedDroneRestriction',
    'LauncherSlotRestriction',
    'LowSlotRestriction',
    'MaxGroupActiveRestriction',
    'MaxGroupFittedRestriction',
    'MaxGroupOnlineRestriction',
    'MediumSlotRestriction',
    'PowerGridRestriction',
    'RigSizeRestriction',
    'RigSlotRestriction',
    'ShipTypeGroupRestriction',
    'SkillRequirementRestriction',
    'StateRestriction',
    'SubsystemIndexRestriction',
    'SubsystemSlotRestriction',
    'TurretSlotRestriction'
]


from .booster_effect import BoosterEffectRestrictionRegister
from .capital_item import CapitalItemRestriction
from .charge_group import ChargeGroupRestriction
from .charge_size import ChargeSizeRestriction
from .charge_volume import ChargeVolumeRestriction
from .drone_group import DroneGroupRestriction
from .item_class import ItemClassRestriction
from .max_group import MaxGroupFittedRestriction, MaxGroupOnlineRestriction, MaxGroupActiveRestriction
from .resource import (
    CpuRestriction, PowerGridRestriction, CalibrationRestriction, DroneBayVolumeRestriction,
    DroneBandwidthRestriction
)
from .rig_size import RigSizeRestriction
from .ship_type_group import ShipTypeGroupRestriction
from .skill_requirement import SkillRequirementRestriction
from .slot_index import SubsystemIndexRestriction, ImplantIndexRestriction, BoosterIndexRestriction
from .slot_amount import (
    HighSlotRestriction, MediumSlotRestriction, LowSlotRestriction, RigSlotRestriction, SubsystemSlotRestriction,
    TurretSlotRestriction, LauncherSlotRestriction, LaunchedDroneRestriction
)
from .state import StateRestriction
