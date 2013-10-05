#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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


from .capitalItem import CapitalItemRegister
from .chargeGroup import ChargeGroupRegister
from .chargeSize import ChargeSizeRegister
from .chargeVolume import ChargeVolumeRegister
from .droneGroup import DroneGroupRegister
from .holderClass import HolderClassRegister
from .launchedDrone import LaunchedDroneRegister
from .maxGroup import MaxGroupFittedRegister, MaxGroupOnlineRegister, MaxGroupActiveRegister
from .resource import CpuRegister, PowerGridRegister, CalibrationRegister, DroneBayVolumeRegister, \
DroneBandwidthRegister
from .rigSize import RigSizeRegister
from .shipTypeGroup import ShipTypeGroupRegister
from .skillRequirement import SkillRequirementRegister
from .slotIndex import SubsystemIndexRegister, ImplantIndexRegister, BoosterIndexRegister
from .slotAmount import HighSlotRegister, MediumSlotRegister, LowSlotRegister, RigSlotRegister, \
SubsystemSlotRegister, TurretSlotRegister, LauncherSlotRegister
from .state import StateRegister

__all__ = ['CapitalItemRegister', 'ChargeGroupRegister', 'ChargeSizeRegister', 'ChargeVolumeRegister',
           'DroneGroupRegister', 'HolderClassRegister', 'LaunchedDroneRegister', 'MaxGroupFittedRegister',
           'MaxGroupOnlineRegister', 'MaxGroupActiveRegister', 'CpuRegister', 'PowerGridRegister',
           'CalibrationRegister', 'DroneBayVolumeRegister', 'DroneBandwidthRegister', 'RigSizeRegister',
           'ShipTypeGroupRegister', 'SkillRequirementRegister', 'SubsystemIndexRegister', 'ImplantIndexRegister',
           'BoosterIndexRegister', 'HighSlotRegister', 'MediumSlotRegister', 'LowSlotRegister',
           'RigSlotRegister', 'SubsystemSlotRegister', 'TurretSlotRegister', 'LauncherSlotRegister',
           'StateRegister']
