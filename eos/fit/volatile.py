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


from .pubsub.message import (
    InputDefaultIncomingDamageChanged, InputEffectsRunModeChanged,
    InputItemAdded, InputItemRemoved, InputSkillLevelChanged,
    InputSourceChanged, InputStateChanged)
from .pubsub.subscriber import BaseSubscriber
from eos.util.volatile_cache import (
    CooperativeVolatileMixin, InheritableVolatileMixin)


class FitVolatileManager(BaseSubscriber):
    """Manage on-fit objects with volatile data.

    Tracks objects which potentially may carry volatile data and clear volatile
    data when requested.

    Args:
        msg_broker: Object which handles message publication and subscriptions.
        volatiles (optional): Iterable with objects which carry volatile
            attributes, which will be tracked permanently. By default we assume
            there're no such objects.
    """

    def __init__(self, msg_broker, volatiles=()):
        self.__msg_broker = msg_broker
        self.__volatile_objects = set()
        msg_broker._subscribe(self, self._handler_map.keys())
        for volatile in volatiles:
            self.__add_volatile_object(volatile)

    # Message handling
    def _handle_item_addition(self, message):
        self.__add_volatile_object(message.item)
        self.__clear_volatile_attrs()

    def _handle_item_removal(self, message):
        self.__clear_volatile_attrs()
        self.__remove_volatile_object(message.item)

    def _handle_other_changes(self, _):
        self.__clear_volatile_attrs()

    _handler_map = {
        InputItemAdded: _handle_item_addition,
        InputItemRemoved: _handle_item_removal,
        InputStateChanged: _handle_other_changes,
        InputEffectsRunModeChanged: _handle_other_changes,
        InputSkillLevelChanged: _handle_other_changes,
        InputSourceChanged: _handle_other_changes,
        InputDefaultIncomingDamageChanged: _handle_other_changes
    }

    # Private methods for message handlers
    def __add_volatile_object(self, object):
        if isinstance(
                object, (InheritableVolatileMixin, CooperativeVolatileMixin)):
            self.__volatile_objects.add(object)

    def __remove_volatile_object(self, object):
        self.__volatile_objects.discard(object)

    def __clear_volatile_attrs(self):
        """Clear volatile data.

        Go through objects in internal storage and clear volatile attribs stored
        on them.
        """
        for volatile in self.__volatile_objects:
            volatile._clear_volatile_attrs()
