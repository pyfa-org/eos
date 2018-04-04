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


from .capital_item import CapitalItemRestrictionRegister
from .charge_group import ChargeGroupRestrictionRegister
from .charge_size import ChargeSizeRestrictionRegister
from .charge_volume import ChargeVolumeRestrictionRegister
from .drone_group import DroneGroupRestrictionRegister
from .item_class import ItemClassRestriction
from .loaded_item import LoadedItemRestriction
from .max_group import MaxGroupActiveRestrictionRegister
from .max_group import MaxGroupFittedRestrictionRegister
from .max_group import MaxGroupOnlineRestrictionRegister
from .resource import CalibrationRestriction
from .resource import CpuRestriction
from .resource import DroneBandwidthRestriction
from .resource import DroneBayVolumeRestriction
from .resource import PowergridRestriction
from .rig_size import RigSizeRestrictionRegister
from .ship_type_group import ShipTypeGroupRestrictionRegister
from .skill_requirement import SkillRequirementRestrictionRegister
from .slot_index import BoosterIndexRestrictionRegister
from .slot_index import ImplantIndexRestrictionRegister
from .slot_index import SubsystemIndexRestrictionRegister
from .slot_quantity import FighterSquadHeavyRestriction
from .slot_quantity import FighterSquadLightRestriction
from .slot_quantity import FighterSquadRestriction
from .slot_quantity import FighterSquadSupportRestriction
from .slot_quantity import HighSlotRestriction
from .slot_quantity import LaunchedDroneRestriction
from .slot_quantity import LauncherSlotRestriction
from .slot_quantity import LowSlotRestriction
from .slot_quantity import MidSlotRestriction
from .slot_quantity import RigSlotRestriction
from .slot_quantity import SubsystemSlotRestriction
from .slot_quantity import TurretSlotRestriction
from .state import StateRestrictionRegister
