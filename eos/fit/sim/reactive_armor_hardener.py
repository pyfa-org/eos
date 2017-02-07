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


from eos.const.eos import State
from eos.const.eve import Attribute, Effect
from eos.fit.messages import ItemAdded, ItemRemoved, ItemStateChanged
from eos.util.pubsub import BaseSubscriber


class ReactiveArmorHardenerSimulator(BaseSubscriber):

    def __init__(self, fit):
        self.__rah_items = set()
        self.__fit = fit
        fit._subscribe(self, self._handler_map.keys())

    def run_simulation(self):
        # Reset attributes on all known RAHs
        for rah in self.__rah_items:
            for attr in ():
                pass

    def get_next_profile(self, current_profile, received_damage):
        pass

    # TODO: for now all message handling is dirty, but will be
    # reworked after i change state and effect handling on item level
    def _handle_item_addition(self, message):
        if self.__check_if_rah(message.item) is True and message.item.state >= State.active:
            self.__rah_items.add(message.item)

    def _handle_item_removal(self, message):
        self.__rah_items.discard(message.item)

    def _handle_state_switch(self, message):
        if self.__check_if_rah(message.item) is not True:
            return
        old_state, new_state = message.old, message.new
        if old_state < State.active and new_state >= State.active:
            self.__rah_items.add(message.item)
        elif new_state < State.active and old_state >= State.active:
            self.__rah_items.discard(message.item)

    _handler_map = {
        ItemAdded: _handle_item_addition,
        ItemRemoved: _handle_item_removal,
        ItemStateChanged: _handle_state_switch
    }

    def _notify(self, message):
        try:
            handler = self._handler_map[type(message)]
        except KeyError:
            return
        handler(self, message)

    def __check_if_rah(self, item):
        for effect in item._eve_type.effects:
            if effect.id == Effect.adaptive_armor_hardener:
                return True
        return False
