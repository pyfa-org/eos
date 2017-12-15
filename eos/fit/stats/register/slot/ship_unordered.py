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


from eos.const.eve import AttrId
from eos.const.eve import EffectId
from eos.fit.item import Ship
from eos.fit.message import EffectsStarted
from eos.fit.message import EffectsStopped
from eos.fit.message import ItemAdded
from eos.fit.message import ItemRemoved
from .base import BaseSlotStatRegister


class UnorderedShipSlotStatRegister(BaseSlotStatRegister):

    def __init__(self, msg_broker, slot_effect_id, slot_attr_id):
        BaseSlotStatRegister.__init__(self)
        self.__slot_effect_id = slot_effect_id
        self.__slot_attr_id = slot_attr_id
        self.__current_ship = None
        self.__slot_users = set()
        msg_broker._subscribe(self, self._handler_map.keys())

    @property
    def used(self):
        return len(self.__slot_users)

    @property
    def total(self):
        try:
            return int(self.__current_ship.attrs[self.__slot_attr_id])
        except (AttributeError, KeyError):
            return None

    @property
    def _users(self):
        return self.__slot_users

    def _handle_item_added(self, msg):
        if isinstance(msg.item, Ship):
            self.__current_ship = msg.item

    def _handle_item_removed(self, msg):
        if msg.item is self.__current_ship:
            self.__current_ship = None

    def _handle_effects_started(self, msg):
        if self.__slot_effect_id in msg.effect_ids:
            self.__slot_users.add(msg.item)

    def _handle_effects_stopped(self, msg):
        if self.__slot_effect_id in msg.effect_ids:
            self.__slot_users.discard(msg.item)

    _handler_map = {
        ItemAdded: _handle_item_added,
        ItemRemoved: _handle_item_removed,
        EffectsStarted: _handle_effects_started,
        EffectsStopped: _handle_effects_stopped}


class RigSlotStatRegister(UnorderedShipSlotStatRegister):

    def __init__(self, msg_broker):
        UnorderedShipSlotStatRegister.__init__(
            self, msg_broker, EffectId.rig_slot, AttrId.rig_slots)


class SubsystemSlotStatRegister(UnorderedShipSlotStatRegister):

    def __init__(self, msg_broker):
        UnorderedShipSlotStatRegister.__init__(
            self, msg_broker, EffectId.subsystem, AttrId.max_subsystems)


class TurretSlotStatRegister(UnorderedShipSlotStatRegister):

    def __init__(self, msg_broker):
        UnorderedShipSlotStatRegister.__init__(
            self, msg_broker, EffectId.turret_fitted, AttrId.turret_slots_left)


class LauncherSlotStatRegister(UnorderedShipSlotStatRegister):

    def __init__(self, msg_broker):
        UnorderedShipSlotStatRegister.__init__(
            self, msg_broker, EffectId.launcher_fitted,
            AttrId.launcher_slots_left)
