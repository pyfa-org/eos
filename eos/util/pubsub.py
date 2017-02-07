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


"""
Implementation of publish-subscribe pattern.
"""


from abc import ABCMeta, abstractmethod
from enum import IntEnum, unique


@unique
class SubscriberPriority(IntEnum):
    high = 1
    normal = 2
    low = 3


class MessageBroker:
    """
    Manages subscriptions and dispatches received
    publications according to active subscriptions.
    """

    def __init__(self):
        # Format: {event class: {priority: subscribers}}
        self.__subscribers = {}

    def _subscribe(self, subscriber, message_types, priority=SubscriberPriority.normal):
        """
        Register subscriber for passed message types.
        """
        for message_type in message_types:
            subscribers_for_priority = self.__subscribers.setdefault(message_type, {}).setdefault(priority, set())
            subscribers_for_priority.add(subscriber)

    def _unsubscribe(self, subscriber, message_types):
        """
        Unregister subscriber from passed message types.
        """
        message_types_to_remove = set()
        for message_type in message_types:
            try:
                subscribers_all = self.__subscribers[message_type]
            except KeyError:
                continue
            priority_to_remove = set()
            for priority, subscribers_for_priority in subscribers_all.items():
                subscribers_for_priority.discard(subscriber)
                if len(subscribers_for_priority) == 0:
                    priority_to_remove.add(priority)
            for priority in priority_to_remove:
                del subscribers_all[priority]
            if len(subscribers_all) == 0:
                message_types_to_remove.add(message_type)
        for message_type in message_types_to_remove:
            del self.__subscribers[message_type]

    def _publish(self, message):
        """
        Publish message and make sure that all
        interested subscribers are notified.
        """
        subscribers = self.__subscribers.get(type(message), ())
        for priority in sorted(subscribers):
            for subscriber in subscribers[priority]:
                subscriber._notify(message)


class BaseSubscriber(metaclass=ABCMeta):
    """
    Base class for subscribers. Forces them to
    implement methods all subscribers should have.
    """

    @abstractmethod
    def _notify(self, message):
        ...
