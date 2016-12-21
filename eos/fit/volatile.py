# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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


from .messages import *
from eos.util.volatile_cache import InheritableVolatileMixin, CooperativeVolatileMixin


class FitVolatileManager:
    """
    Class which tracks on-fit objects with volatile
    data and clears this data when requested.

    Required arguments:
    msg_broker -- object which handles message publication
    and subscriptions

    Optional arguments:
    volatiles -- iterable with objects which carry volatile
    attributes, which will be tracked permanently
    """

    def __init__(self, msg_broker, volatiles=()):
        self.__msg_broker = msg_broker
        self.__volatile_objects = set()
        msg_broker._subscribe(self, self._handler_map.keys())
        for volatile in volatiles:
            self.__add_volatile_object(volatile)

    # Message handling
    def _handle_holder_addition(self, message):
        self.__add_volatile_object(message.holder)
        self.__clear_volatile_attrs()

    def _handle_holder_removal(self, message):
        self.__clear_volatile_attrs()
        self.__remove_volatile_object(message.holder)

    def _handle_other_changes(self, message):
        self.__clear_volatile_attrs()

    _handler_map = {
        HolderAdded: _handle_holder_addition,
        HolderRemoved: _handle_holder_removal,
        HolderStateChanged: _handle_other_changes,
        EffectsEnabled: _handle_other_changes,
        EffectsDisabled: _handle_other_changes,
        SourceChanged: _handle_other_changes,
        SkillLevelChanged: _handle_other_changes
    }

    def _notify(self, message):
        try:
            handler = self._handler_map[type(message)]
        except KeyError:
            return
        handler(self, message)

    # Private methods for message handlers
    def __add_volatile_object(self, object):
        """
        Add passed object to internal storage in case it
        carries any volatile attributes.
        """
        if isinstance(object, (InheritableVolatileMixin, CooperativeVolatileMixin)):
            self.__volatile_objects.add(object)

    def __remove_volatile_object(self, object):
        """
        Remove passed object from internal storage
        """
        self.__volatile_objects.discard(object)

    def __clear_volatile_attrs(self):
        """
        Go through objects in internal storage and clear
        volatile attribs stored on them.
        """
        for volatile in self.__volatile_objects:
            volatile._clear_volatile_attrs()
