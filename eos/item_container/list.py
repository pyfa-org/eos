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


from numbers import Integral

from .base import ItemContainerBase
from .exception import ItemAlreadyAssignedError
from .exception import SlotTakenError


class ItemList(ItemContainerBase):
    """Ordered container for items.

    Implements list-like interface.

    Args:
        parent: Object, to which this container is attached.
        item_class: Class of items this container is allowed to contain.
    """

    def __init__(self, parent, item_class):
        ItemContainerBase.__init__(self, item_class)
        self.__parent = parent
        self.__list = []

    # Modifying methods
    def insert(self, index, value):
        """Insert value to given position.

        If position is out of range of container and value is item, fill
        container with Nones up to position and put item there.

        Args:
            index: Position to insert value to.
            value: Item or None. None can be used to insert empty slots between
                items.

        Raises:
            TypeError: If item of unacceptable class is passed.
            ValueError: If item is passed as value and it cannot be added to
                the container (e.g. already belongs to other container).
        """
        self._check_class(value, allow_none=True)
        self._allocate(index - 1)
        self.__list.insert(index, value)
        if value is None:
            self._cleanup()
        else:
            try:
                self._handle_item_addition(value, self)
            except ItemAlreadyAssignedError as e:
                del self.__list[index]
                self._cleanup()
                raise ValueError(*e.args) from e

    def append(self, item):
        """Append item to the end of the container.

        Args:
            item: Item to append.

        Possible exceptions:
            TypeError: If item of unacceptable class is passed.
            ValueError: If item cannot be added to the container (e.g. already
                belongs to other container).
        """
        self._check_class(item)
        self.__list.append(item)
        try:
            self._handle_item_addition(item, self)
        except ItemAlreadyAssignedError as e:
            del self.__list[-1]
            raise ValueError(*e.args) from e

    def place(self, index, item):
        """Put item to given position.

        If position is out of range of container, fill it with Nones up to
        position and put item there.

        Args:
            index: Position to put item to.
            item: Item to put.

        Raises:
            TypeError: If item of unacceptable class is passed.
            ValueError: If item cannot be added to the container (e.g. already
                belongs to other container).
            SlotTakenError: If slot at specified index is already taken by other
                item.
        """
        self._check_class(item)
        try:
            old_item = self.__list[index]
        except IndexError:
            self._allocate(index)
        else:
            if old_item is not None:
                raise SlotTakenError(index)
        self.__list[index] = item
        try:
            self._handle_item_addition(item, self)
        except ItemAlreadyAssignedError as e:
            self.__list[index] = None
            self._cleanup()
            raise ValueError(*e.args) from e

    def equip(self, item):
        """Put item to first free slot in container.

        If container doesn't have free slots, append item to the end of the
        container.

        Args:
            item: Item to put.

        Raises:
            TypeError: If item of unacceptable class is passed.
            ValueError: If item cannot be added to the container (e.g. already
                belongs to other container).
        """
        self._check_class(item)
        try:
            index = self.__list.index(None)
        except ValueError:
            index = len(self.__list)
            self.__list.append(item)
        else:
            self.__list[index] = item
        try:
            self._handle_item_addition(item, self)
        except ItemAlreadyAssignedError as e:
            self.__list[index] = None
            self._cleanup()
            raise ValueError(*e.args) from e

    def remove(self, value):
        """
        Remove item or None from the container.

        Also clean container's tail if it's filled with Nones.

        Args:
            value: Thing to remove. Can be item, None or integer index.

        Raises:
            ValueError: If passed item cannot be found in container.
            IndexError: If passed index is out of range of list.
        """
        if isinstance(value, Integral):
            index = value
            item = self.__list[index]
        else:
            item = value
            index = self.__list.index(item)
        if item is not None:
            self._handle_item_removal(item)
        del self.__list[index]
        self._cleanup()

    def free(self, value):
        """Free item's slot.

        Or, in other words, replace it with None, without shifting list tail.
        Also clean container's tail after replacement, if it's filled with
        Nones.

        Args:
            value: Thing to remove. Can be item or integer index.

        Raises:
            ValueError: If passed item cannot be found in container.
            IndexError: If passed index is out of range of the list.
        """
        if isinstance(value, Integral):
            index = value
            item = self.__list[index]
        else:
            item = value
            index = self.__list.index(item)
        if item is None:
            return
        self._handle_item_removal(item)
        self.__list[index] = None
        self._cleanup()

    def clear(self):
        """Remove everything from the container."""
        for item in self.__list:
            if item is not None:
                self._handle_item_removal(item)
        self.__list.clear()

    # Non-modifying methods
    def __getitem__(self, index):
        """Get item by index or items by slice object."""
        return self.__list.__getitem__(index)

    def index(self, value):
        """Get index of value.

        Args:
            value: Item or None. In case of None, searches for first seen None.
        """
        return self.__list.index(value)

    def items(self):
        """Return item view over the container."""
        return ListItemView(self.__list)

    def __iter__(self):
        return iter(self.__list)

    def __contains__(self, value):
        return value in self.__list

    def __len__(self):
        return len(self.__list)

    # Auxiliary methods
    def _allocate(self, index):
        """Complete list with Nones until passed index becomes accessible.

        Used by other methods if index requested by user is out of range.
        """
        allocated_num = len(self.__list)
        self.__list.extend([None] * max(index - allocated_num + 1, 0))

    def _cleanup(self):
        """Remove trailing Nones from list."""
        try:
            while self.__list[-1] is None:
                del self.__list[-1]
        # If we get IndexError, we've ran out of list elements and we're fine
        # with it
        except IndexError:
            pass

    @property
    def _fit(self):
        return self.__parent._fit

    def __repr__(self):
        return repr(self.__list)


class ListItemView:
    """Item view over passed list container.

    Item view allows you to deal just with items in the list, ignoring empty
    slots.
    """

    def __init__(self, list_):
        self.__list = list_

    def __iter__(self):
        for item in self.__list:
            if item is None:
                continue
            yield item

    def __contains__(self, value):
        if value is None:
            return False
        return self.__list.__contains__(value)

    def __len__(self):
        return sum(item is not None for item in self.__list)
