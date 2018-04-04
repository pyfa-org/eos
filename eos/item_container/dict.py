# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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


from .set import ItemSet


class ItemDict:
    """Dict-like container for items.

    It contains items keyed against something.

    Args:
        parent: Object, to which this container is attached.
        item_class: Class of items this container is allowed to contain.
        container_override (optional): When this argument is set, its value will
            be assigned as container to all items being added.
    """

    def __init__(self, parent, item_class, container_override=None):
        self.__item_set = ItemSet(
            parent, item_class, container_override=container_override)
        self.__keyed_items = {}

    # Modifying methods
    def __setitem__(self, key, item):
        """Add item to the container against key.

        Args:
            key: Key, against which item should be added.
            item: Item to add.

        Raises:
            TypeError: If item of unacceptable class is passed.
            ValueError: If item cannot be added to the container (e.g. already
                belongs to other container or item with this key exists in the
                container).
        """
        self.__item_set._check_class(item)
        if key in self.__keyed_items:
            msg = 'item with key {} already exists in this dict'.format(key)
            raise ValueError(msg)
        self.__keyed_items[key] = item
        try:
            self.__item_set.add(item)
        except (TypeError, ValueError):
            del self.__keyed_items[key]
            raise

    def __delitem__(self, key):
        """Remove item from the container via its key.

        Args:
            key: If item is stored against this key, it will be removed.

        Raises:
            KeyError: If item cannot be removed from the container (e.g. it
                doesn't belong to it).
        """
        # Should raise KeyError if there's no such item
        item = self.__keyed_items[key]
        self.__item_set.remove(item)
        del self.__keyed_items[key]

    def clear(self):
        """Remove everything from the container."""
        self.__item_set.clear()
        self.__keyed_items.clear()

    # Non-modifying methods
    def __getitem__(self, key):
        return self.__keyed_items[key]

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self):
        return self.__keyed_items.keys()

    def values(self):
        return self.__keyed_items.values()

    def items(self):
        return self.__keyed_items.items()

    def __contains__(self, key):
        return key in self.__keyed_items

    def __iter__(self):
        return iter(self.__keyed_items)

    def __len__(self):
        return len(self.__keyed_items)

    # Auxiliary methods
    def __repr__(self):
        return repr(self.__keyed_items)
