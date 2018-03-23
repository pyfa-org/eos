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


from abc import ABCMeta
from abc import abstractmethod

from eos.const.eve import AttrId
from eos.const.eve import EffectId
from eos.fit.message import EffectsStarted
from eos.fit.message import EffectsStopped
from .base import BaseSlotRegister


class HardpointEffectSlotRegister(BaseSlotRegister, metaclass=ABCMeta):

    def __init__(self, fit):
        BaseSlotRegister.__init__(self)
        self.__fit = fit
        self.__slot_users = set()
        fit._subscribe(self, self._handler_map.keys())

    @property
    @abstractmethod
    def _slot_effect_id(self):
        ...

    @property
    @abstractmethod
    def _slot_attr_id(self):
        ...

    @property
    def used(self):
        return len(self.__slot_users)

    @property
    def total(self):
        try:
            return int(self.__fit.ship.attrs[self._slot_attr_id])
        except (AttributeError, KeyError):
            return 0

    @property
    def _users(self):
        return self.__slot_users

    def _handle_effects_started(self, msg):
        if self._slot_effect_id in msg.effect_ids:
            self.__slot_users.add(msg.item)

    def _handle_effects_stopped(self, msg):
        if self._slot_effect_id in msg.effect_ids:
            self.__slot_users.discard(msg.item)

    _handler_map = {
        EffectsStarted: _handle_effects_started,
        EffectsStopped: _handle_effects_stopped}


class TurretSlotRegister(HardpointEffectSlotRegister):

    _slot_effect_id = EffectId.turret_fitted
    _slot_attr_id = AttrId.turret_slots_left


class LauncherSlotRegister(HardpointEffectSlotRegister):

    _slot_effect_id = EffectId.launcher_fitted
    _slot_attr_id = AttrId.launcher_slots_left
