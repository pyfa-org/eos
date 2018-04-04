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


class TypeUniqueItemSet(ItemSet):
    """Unordered container for items with additional restriction.

    This container can't hold two items with the same type ID, and provides
    access to items via their type IDs.

    Args:
        parent: Object, to which this container is attached.
        item_class: Class of items this container is allowed to contain.
    """

    def __init__(self, parent, item_class):
        ItemSet.__init__(self, parent, item_class)
        self.__type_id_map = {}

    # Modifying methods
    def add(self, item):
        """Add item to the container.

        Args:
            item: Item to add.

        Raises:
            TypeError: If item of unacceptable class is passed.
            ValueError: If item cannot be added to the container (e.g. already
                belongs to other container or item with this type ID exists in
                the container).
        """
        self._check_class(item)
        type_id = item._type_id
        if type_id in self.__type_id_map:
            msg = (
                'item with type ID {} already exists in this set'
            ).format(type_id)
            raise ValueError(msg)
        self.__type_id_map[type_id] = item
        try:
            ItemSet.add(self, item)
        except (TypeError, ValueError):
            del self.__type_id_map[type_id]
            raise

    def remove(self, item):
        """Remove item from the container.

        Args:
            item: Item to remove.

        Raises:
            KeyError: If item cannot be removed from the container (e.g. it
                doesn't belong to it).
        """
        ItemSet.remove(self, item)
        del self.__type_id_map[item._type_id]

    def __delitem__(self, type_id):
        """Remove item by type ID."""
        item = self.__type_id_map[type_id]
        self.remove(item)

    def clear(self):
        """Remove everything from the container."""
        ItemSet.clear(self)
        self.__type_id_map.clear()

    # Non-modifying methods
    def __getitem__(self, type_id):
        """Get item by type ID."""
        return self.__type_id_map[type_id]

    def __contains__(self, value):
        """Check if type ID or item are present in set."""
        return (
            value in self.__type_id_map or
            ItemSet.__contains__(self, value))

    # Auxiliary methods
    def __repr__(self):
        return repr(self.__type_id_map)
