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
    'CapitalItemRestrictionRegister',
    'ChargeGroupRestrictionRegister',
    'ChargeSizeRestrictionRegister',
    'ChargeVolumeRestrictionRegister',
    'DroneGroupRestrictionRegister',
    'ItemClassRestrictionRegister',
    'MaxGroupFittedRegister',
    'MaxGroupOnlineRegister',
    'MaxGroupActiveRegister',
    'CpuRegister',
    'PowerGridRegister',
    'CalibrationRegister',
    'DroneBayVolumeRegister',
    'DroneBandwidthRegister',
    'RigSizeRestrictionRegister',
    'ShipTypeGroupRestrictionRegister',
    'SkillRequirementRestrictionRegister',
    'SubsystemIndexRegister',
    'ImplantIndexRegister',
    'BoosterIndexRegister',
    'HighSlotRegister',
    'MediumSlotRegister',
    'LowSlotRegister',
    'RigSlotRegister',
    'SubsystemSlotRegister',
    'TurretSlotRegister',
    'LauncherSlotRegister',
    'LaunchedDroneRegister',
    'StateRestrictionRegister'
]


from .booster_effect import BoosterEffectRestrictionRegister
from .capital_item import CapitalItemRestrictionRegister
from .charge_group import ChargeGroupRestrictionRegister
from .charge_size import ChargeSizeRestrictionRegister
from .charge_volume import ChargeVolumeRestrictionRegister
from .drone_group import DroneGroupRestrictionRegister
from .item_class import ItemClassRestrictionRegister
from .max_group import MaxGroupFittedRegister, MaxGroupOnlineRegister, MaxGroupActiveRegister
from .resource import (CpuRegister, PowerGridRegister, CalibrationRegister, DroneBayVolumeRegister,
    DroneBandwidthRegister)
from .rig_size import RigSizeRestrictionRegister
from .ship_type_group import ShipTypeGroupRestrictionRegister
from .skill_requirement import SkillRequirementRestrictionRegister
from .slot_index import SubsystemIndexRegister, ImplantIndexRegister, BoosterIndexRegister
from .slot_amount import (HighSlotRegister, MediumSlotRegister, LowSlotRegister, RigSlotRegister,
    SubsystemSlotRegister, TurretSlotRegister, LauncherSlotRegister, LaunchedDroneRegister)
from .state import StateRestrictionRegister
