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


class MessageBroker:
    """Manages message subscriptions and dispatch messages to recipients."""

    def __init__(self):
        # Format: {event class: {subscribers}}
        self.__subscribers = {}

    def _subscribe(self, subscriber, message_types):
        """Register subscriber for passed message types."""
        for message_type in message_types:
            self.__subscribers.setdefault(message_type, set()).add(subscriber)

    def _unsubscribe(self, subscriber, message_types):
        """Unregister subscriber from passed message types."""
        msgtypes_to_remove = set()
        for message_type in message_types:
            try:
                subscribers = self.__subscribers[message_type]
            except KeyError:
                continue
            subscribers.discard(subscriber)
            if not subscribers:
                msgtypes_to_remove.add(message_type)
        for message_type in msgtypes_to_remove:
            del self.__subscribers[message_type]

    def _publish(self, message):
        """Publish single message."""
        for subscriber in self.__subscribers.get(type(message), ()):
            subscriber._notify(message)

    def _publish_bulk(self, messages):
        """Publish multiple messages."""
        for message in messages:
            for subscriber in self.__subscribers.get(type(message), ()):
                subscriber._notify(message)
