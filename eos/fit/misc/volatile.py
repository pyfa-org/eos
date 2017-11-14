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


from eos.util.volatile_cache import (
    CooperativeVolatileMixin, InheritableVolatileMixin)


class VolatileMgr:
    """Manage on-fit objects with volatile data.

    Tracks objects which potentially may carry volatile data and clears volatile
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
        for volatile in volatiles:
            self.add_volatile_object(volatile)

    # Private methods for message handlers
    def add_volatile_object(self, object):
        if isinstance(
                object, (InheritableVolatileMixin, CooperativeVolatileMixin)):
            self.__volatile_objects.add(object)

    def remove_volatile_object(self, object):
        self.__volatile_objects.discard(object)

    def clear_volatile_attrs(self):
        """Clear volatile data.

        Go through objects in internal storage and clear volatile attributes
        stored on them.
        """
        for volatile in self.__volatile_objects:
            volatile._clear_volatile_attrs()
