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


from eos.const.eos import Slot
from eos.fit.item import Drone
from .base import BaseStatRegister


class SlotUseRegister(BaseStatRegister):
    """
    Class which implements common functionality for all
    registers, which are used to calculate amount of
    resource used.
    """

    def __init__(self, fit):
        self._fit = fit
        self.__slot_users = set()

    def register_item(self, holder):
        self.__slot_users.add(holder)

    def unregister_item(self, holder):
        self.__slot_users.discard(holder)

    def __len__(self):
        return len(self.__slot_users)


class TurretUseRegister(SlotUseRegister):
    """
    Assist with calculation of amount of used turret slots.
    """

    def register_item(self, holder):
        if Slot.turret in holder._eve_type.slots:
            SlotUseRegister.register_item(self, holder)


class LauncherUseRegister(SlotUseRegister):
    """
    Assist with calculation of amount of used launcher slots.
    """

    def register_item(self, holder):
        if Slot.launcher in holder._eve_type.slots:
            SlotUseRegister.register_item(self, holder)


class LaunchedDroneRegister(SlotUseRegister):
    """
    Assist with calculation of amount of launched drones.
    """

    def register_item(self, holder):
        if isinstance(holder, Drone):
            SlotUseRegister.register_item(self, holder)
