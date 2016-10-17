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


from .capital_item import CapitalItemRegister
from .charge_group import ChargeGroupRegister
from .charge_size import ChargeSizeRegister
from .charge_volume import ChargeVolumeRegister
from .drone_group import DroneGroupRegister
from .holder_class import HolderClassRegister
from .max_group import MaxGroupFittedRegister, MaxGroupOnlineRegister, MaxGroupActiveRegister
from .resource import CpuRegister, PowerGridRegister, CalibrationRegister, DroneBayVolumeRegister, \
    DroneBandwidthRegister
from .rig_size import RigSizeRegister
from .ship_type_group import ShipTypeGroupRegister
from .skill_requirement import SkillRequirementRegister
from .slot_index import SubsystemIndexRegister, ImplantIndexRegister, BoosterIndexRegister
from .slot_amount import HighSlotRegister, MediumSlotRegister, LowSlotRegister, RigSlotRegister, \
    SubsystemSlotRegister, TurretSlotRegister, LauncherSlotRegister, LaunchedDroneRegister
from .state import StateRegister


__all__ = [
    'CapitalItemRegister',
    'ChargeGroupRegister',
    'ChargeSizeRegister',
    'ChargeVolumeRegister',
    'DroneGroupRegister',
    'HolderClassRegister',
    'MaxGroupFittedRegister',
    'MaxGroupOnlineRegister',
    'MaxGroupActiveRegister',
    'CpuRegister',
    'PowerGridRegister',
    'CalibrationRegister',
    'DroneBayVolumeRegister',
    'DroneBandwidthRegister',
    'RigSizeRegister',
    'ShipTypeGroupRegister',
    'SkillRequirementRegister',
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
    'StateRegister'
]
