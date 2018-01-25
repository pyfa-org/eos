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
from eos.fit.item import Ship
from eos.fit.message import EffectsStarted
from eos.fit.message import EffectsStopped
from eos.fit.message import ItemAdded
from eos.fit.message import ItemRemoved
from .base import BaseResourceRegister


class ShipRegularResourceRegister(BaseResourceRegister, metaclass=ABCMeta):

    def __init__(self, msg_broker):
        BaseResourceRegister.__init__(self)
        self.__current_ship = None
        self.__resource_users = set()
        msg_broker._subscribe(self, self._handler_map.keys())

    @property
    @abstractmethod
    def _output_attr_id(self):
        ...

    @property
    @abstractmethod
    def _use_effect_id(self):
        ...

    @property
    @abstractmethod
    def _use_attr_id(self):
        ...

    @property
    def used(self):
        return sum(
            item.attrs[self._use_attr_id]
            for item in self.__resource_users)

    @property
    def output(self):
        try:
            return self.__current_ship.attrs[self._output_attr_id]
        except (AttributeError, KeyError):
            return None

    @property
    def _users(self):
        return self.__resource_users

    def _handle_item_added(self, msg):
        if isinstance(msg.item, Ship):
            self.__current_ship = msg.item

    def _handle_item_removed(self, msg):
        if msg.item is self.__current_ship:
            self.__current_ship = None

    def _handle_effects_started(self, msg):
        if (
            self._use_effect_id in msg.effect_ids and
            self._use_attr_id in msg.item._type_attrs
        ):
            self.__resource_users.add(msg.item)

    def _handle_effects_stopped(self, msg):
        if self._use_effect_id in msg.effect_ids:
            self.__resource_users.discard(msg.item)

    _handler_map = {
        ItemAdded: _handle_item_added,
        ItemRemoved: _handle_item_removed,
        EffectsStarted: _handle_effects_started,
        EffectsStopped: _handle_effects_stopped}


class RoundedShipRegularResourceRegister(ShipRegularResourceRegister):

    @property
    def used(self):
        return round(super().used, 2)


class CalibrationRegister(ShipRegularResourceRegister):

    _output_attr_id = AttrId.upgrade_capacity
    _use_effect_id = EffectId.rig_slot
    _use_attr_id = AttrId.upgrade_cost


class CpuRegister(RoundedShipRegularResourceRegister):

    _output_attr_id = AttrId.cpu_output
    _use_effect_id = EffectId.online
    _use_attr_id = AttrId.cpu


class PowergridRegister(RoundedShipRegularResourceRegister):

    _output_attr_id = AttrId.power_output
    _use_effect_id = EffectId.online
    _use_attr_id = AttrId.power
