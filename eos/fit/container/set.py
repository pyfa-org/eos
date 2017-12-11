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

    Args:
        owner: Object, to which this container is attached.
        item_class: Class of items this container is allowed to contain.
    """

    def __init__(self, owner, item_class):
        ItemContainerBase.__init__(self, item_class)
        self.__owner = owner
        self.__set = set()

    # Modifying methods
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

    # Non-modifying methods
    def __iter__(self):
        return iter(self.__set)

    def __contains__(self, item):
        return item in self.__set

    def __len__(self):
        return len(self.__set)

    # Auxiliary methods
    @property
    def _fit(self):
        return self.__owner._fit

    def __repr__(self):
        return repr(self.__set)
