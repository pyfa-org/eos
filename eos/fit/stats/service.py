# ==============================================================================
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
# ==============================================================================


import math

from eos.const.eve import AttrId
from eos.fit.item import Ship
from eos.fit.message import ItemLoaded
from eos.fit.message import ItemUnloaded
from eos.fit.stats_container import ItemHP
from eos.fit.stats_container import ResistProfile
from eos.fit.stats_container import TankingLayers
from eos.util.pubsub.subscriber import BaseSubscriber
from .register import CalibrationRegister
from .register import CpuRegister
from .register import DmgDealerRegister
from .register import DroneBandwidthRegister
from .register import DronebayVolumeRegister
from .register import FighterSquadHeavyRegister
from .register import FighterSquadLightRegister
from .register import FighterSquadRegister
from .register import FighterSquadSupportRegister
from .register import HighSlotRegister
from .register import LaunchedDroneRegister
from .register import LauncherSlotRegister
from .register import LowSlotRegister
from .register import MediumSlotRegister
from .register import PowergridRegister
from .register import RigSlotRegister
from .register import SubsystemSlotRegister
from .register import TurretSlotRegister


class StatService(BaseSubscriber):
    """Object which is used as access points for all fit statistics.

    Args:
        msg_broker: Message broker which is used to deliver all the messages
            about context changes.
    """

    def __init__(self, msg_broker):
        BaseSubscriber.__init__(self)
        self.__current_ship = None
        self.__dd_reg = DmgDealerRegister(msg_broker)
        # Initialize sub-containers
        self.cpu = CpuRegister(msg_broker)
        self.powergrid = PowergridRegister(msg_broker)
        self.calibration = CalibrationRegister(msg_broker)
        self.dronebay = DronebayVolumeRegister(msg_broker)
        self.drone_bandwidth = DroneBandwidthRegister(msg_broker)
        self.high_slots = HighSlotRegister(msg_broker)
        self.med_slots = MediumSlotRegister(msg_broker)
        self.low_slots = LowSlotRegister(msg_broker)
        self.rig_slots = RigSlotRegister(msg_broker)
        self.subsystem_slots = SubsystemSlotRegister(msg_broker)
        self.turret_slots = TurretSlotRegister(msg_broker)
        self.launcher_slots = LauncherSlotRegister(msg_broker)
        self.launched_drones = LaunchedDroneRegister(msg_broker)
        self.fighter_squads = FighterSquadRegister(msg_broker)
        self.fighter_squads_support = FighterSquadSupportRegister(msg_broker)
        self.fighter_squads_light = FighterSquadLightRegister(msg_broker)
        self.fighter_squads_heavy = FighterSquadHeavyRegister(msg_broker)
        msg_broker._subscribe(self, self._handler_map.keys())

    @property
    def hp(self):
        """Fetch ship HP stats.

        Returns:
            TankingLayersTotal helper container instance. If ship data cannot be
            fetched, HP values will be None.
        """
        try:
            return self.__current_ship.hp
        except AttributeError:
            return ItemHP(0, 0, 0)

    @property
    def resists(self):
        """Fetch ship resistances.

        Returns:
            TankingLayers helper container instance, whose attributes are
            DmgTypes helper container instances. If ship data cannot be fetched,
            resistance values will be None.
        """
        try:
            return self.__current_ship.resists
        except AttributeError:
            null_res = ResistProfile(0, 0, 0, 0)
            return TankingLayers(null_res, null_res, null_res)

    def get_ehp(self, dmg_profile=None):
        """Get effective HP of an item against passed damage profile.

        Args:
            dmg_profile (optional): DmgProfile helper container instance. If
                not specified, default on-fit damage profile is used.

        Returns:
            TankingLayersTotal helper container instance. If ship data cannot be
            fetched, EHP values will be None.
        """
        try:
            return self.__current_ship.get_ehp(dmg_profile)
        except AttributeError:
            return ItemHP(0, 0, 0)

    @property
    def worst_case_ehp(self):
        """Get eve-style effective HP for the item.

        Eve takes the worst resistance and calculates EHP against it, on a per-
        layer basis.

        Returns:
            TankingLayersTotal helper container instance. If ship data cannot be
            fetched, EHP values will be None.
        """
        try:
            return self.__current_ship.worst_case_ehp
        except AttributeError:
            return ItemHP(0, 0, 0)

    def get_volley(self, item_filter=None, tgt_resists=None):
        """
        Get volley of the fit.

        Args:
            item_filter (optional): When iterating over fit items, this function
                is called. If evaluated as True, this item is taken into
                consideration, else not. If argument is None, all items 'pass
                filter'. By default None.
            tgt_resists (optional): ResistanceProfile helper container instance.
                If specified, effective damage against these resistances is
                calculated.

        Returns:
            DmgTypesTotal helper container instance.
        """
        return self.__dd_reg.get_volley(item_filter, tgt_resists)

    def get_dps(self, item_filter=None, reload=False, tgt_resists=None):
        """
        Get DPS of the fit.

        Args:
            item_filter (optional): When iterating over fit items, this function
                is called. If evaluated as True, this item is taken into
                consideration, else not. If argument is None, all items 'pass
                filter'. By default None.
            reload (optional): Boolean flag which controls if reload should be
                taken into consideration or not. By default, reload is ignored.
            tgt_resists (optional): ResistanceProfile helper container instance.
                If specified, effective damage against these resistances is
                calculated.

        Returns:
            DmgTypesTotal helper container instance.
        """
        return self.__dd_reg.get_dps(item_filter, reload, tgt_resists)

    @property
    def agility_factor(self):
        try:
            agility = self.__current_ship.attrs[AttrId.agility]
            mass = self.__current_ship.attrs[AttrId.mass]
        except (AttributeError, KeyError):
            return None
        agility_factor = -math.log(0.25) * agility * mass / 1000000
        return agility_factor

    @property
    def align_time(self):
        try:
            return math.ceil(self.agility_factor)
        except TypeError:
            return None

    def _handle_item_loaded(self, msg):
        if isinstance(msg.item, Ship):
            self.__current_ship = msg.item

    def _handle_item_unloaded(self, msg):
        if msg.item is self.__current_ship:
            self.__current_ship = None

    _handler_map = {
        ItemLoaded: _handle_item_loaded,
        ItemUnloaded: _handle_item_unloaded}
