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


from .base import ItemContainerBase
from .exception import ItemAlreadyAssignedError


class ItemSet(ItemContainerBase):
    """Unordered container for items.

    Implements set-like interface.
    """

    def __init__(self, fit, item_class):
        """Initialize unordered container.

        Args:
            fit: Fit, to which container is attached.
            item_class: Class of items this container is allowed to contain.
        """
        ItemContainerBase.__init__(self, item_class)
        self.__fit = fit
        self.__set = set()

    @property
    def _fit(self):
        return self.__fit

    def add(self, item):
        """Add item to the container.

        Args:
            item: item to add.

        Raises:
            TypeError: If item of unacceptable class is passed.
            ValueError: If item cannot be added to the container (e.g. already
                belongs to some fit).
        """
        self._check_class(item)
        self.__set.add(item)
        try:
            self._handle_item_addition(item, self)
        except ItemAlreadyAssignedError as e:
            self.__set.remove(item)
            raise ValueError from e

    def remove(self, item):
        """Remove item from the container.

        Args:
            item: Item to remove.

        Raises:
            KeyError: If item cannot be removed from the container (e.g. it
                doesn't belong to it).
        """
        if item not in self.__set:
            raise KeyError(item)
        self._handle_item_removal(item)
        self.__set.remove(item)

    def clear(self):
        """Remove everything from the container."""
        for item in self.__set:
            self._handle_item_removal(item)
        self.__set.clear()

    def __iter__(self):
        return self.__set.__iter__()

    def __contains__(self, item):
        return self.__set.__contains__(item)

    def __len__(self):
        return self.__set.__len__()

    def __repr__(self):
        return repr(self.__set)
