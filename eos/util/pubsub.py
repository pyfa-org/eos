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


class MessageBroker:
    """
    Manages subscriptions and dispatches received
    publications according to active subscriptions.
    """

    def __init__(self):
        # Format: {event class: subscribers}
        self.__subscribers = {}

    def _subscribe(self, subscriber, message_types):
        """
        Register subscriber for passed message types.
        """
        for message_type in message_types:
            subscribers = self.__subscribers.setdefault(message_type, set())
            subscribers.add(subscriber)

    def _unsubscribe(self, subscriber, message_types):
        """
        Unregister subscriber from passed message types.
        """
        for message_type in message_types:
            try:
                subscribers = self.__subscribers[message_type]
            except KeyError:
                continue
            subscribers.discard(subscriber)

    def _publish(self, message):
        """
        Publish message and make sure that all
        interested subscribers are notified.
        """
        subscribers = self.__subscribers.get(type(message), ())
        for subscriber in subscribers:
            subscriber._notify(message)


class BaseSubscriber(metaclass=ABCMeta):
    """
    Base class for subscribers. Forces them to
    implement methods all subscribers should have.
    """

    @abstractmethod
    def _notify(self, message):
        ...
