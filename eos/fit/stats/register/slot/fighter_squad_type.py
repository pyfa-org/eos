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
from eos.fit.item import FighterSquad
from eos.fit.item import Ship
from eos.fit.message import ItemLoaded
from eos.fit.message import ItemUnloaded
from .base import BaseSlotRegister


class FighterSquadTypeRegister(BaseSlotRegister, metaclass=ABCMeta):

    def __init__(self, msg_broker):
        BaseSlotRegister.__init__(self)
        self.__current_ship = None
        self.__fighters = set()
        msg_broker._subscribe(self, self._handler_map.keys())

    @property
    @abstractmethod
    def _fighter_attr_id(self):
        ...

    @property
    @abstractmethod
    def _ship_attr_id(self):
        ...

    @property
    def used(self):
        return len(self.__fighters)

    @property
    def total(self):
        try:
            return int(self.__current_ship.attrs[self._ship_attr_id])
        except (AttributeError, KeyError):
            return None

    @property
    def _users(self):
        return self.__fighters

    def _handle_item_loaded(self, msg):
        if (
            isinstance(msg.item, FighterSquad) and
            msg.item._type_attrs.get(self._fighter_attr_id)
        ):
            self.__fighters.add(msg.item)
        elif isinstance(msg.item, Ship):
            self.__current_ship = msg.item

    def _handle_item_unloaded(self, msg):
        if msg.item is self.__current_ship:
            self.__current_ship = None
        self.__fighters.discard(msg.item)

    _handler_map = {
        ItemLoaded: _handle_item_loaded,
        ItemUnloaded: _handle_item_unloaded}


class FighterSquadSupportRegister(FighterSquadTypeRegister):

    _fighter_attr_id = AttrId.fighter_squadron_is_support
    _ship_attr_id = AttrId.fighter_support_slots


class FighterSquadLightRegister(FighterSquadTypeRegister):

    _fighter_attr_id = AttrId.fighter_squadron_is_light
    _ship_attr_id = AttrId.fighter_light_slots


class FighterSquadHeavyRegister(FighterSquadTypeRegister):

    _fighter_attr_id = AttrId.fighter_squadron_is_heavy
    _ship_attr_id = AttrId.fighter_heavy_slots
