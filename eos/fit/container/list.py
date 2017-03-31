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


from numbers import Integral

from eos.fit.pubsub.message import InputItemsPositionChanged
from .base import ItemContainerBase
from .exception import ItemAlreadyAssignedError, SlotTakenError


class ItemList(ItemContainerBase):
    """
    Ordered container for items.

    Required arguments:
    fit -- fit, to which container is attached
    item_class -- class of items this container
        is allowed to contain
    """

    def __init__(self, fit, item_class):
        ItemContainerBase.__init__(self, item_class)
        self.__fit = fit
        self.__list = []

    @property
    def _fit(self):
        return self.__fit

    def insert(self, index, value):
        """
        Insert value to given position; if position is
        out of range of container and value is item,
        fill container with Nones up to position and
        put item there. Also value can be None to
        insert empty slots between items.

        Possible exceptions:
        TypeError -- raised when item of unacceptable class
            is passed
        ValueError -- raised when item is passed as value and
            it cannot be added to container (e.g. already belongs
            to some fit)
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
        # After all the changes, if there're items after the index
        # we're inserting to, items change their positions
        new_positions = {i: self.__list.index(i) for i in self.__list[index + 1:] if i is not None}
        if len(new_positions) > 0:
            self.__fit._publish(InputItemsPositionChanged(new_positions))

    def append(self, item):
        """
        Append item to the end of container.

        Possible exceptions:
        TypeError -- raised when item of unacceptable class
            is passed
        ValueError -- raised when item cannot be added to container
            (e.g. already belongs to some fit)
        """
        self._check_class(item)
        self.__list.append(item)
        try:
            self._handle_item_addition(item, self)
        except ItemAlreadyAssignedError as e:
            del self.__list[-1]
            raise ValueError(*e.args) from e

    def place(self, index, item):
        """
        Put item to given position; if position is out of
        range of container, fill it with Nones up to position
        and put item there.

        Possible exceptions:
        TypeError -- raised when item of unacceptable class
            is passed
        ValueError -- raised when item cannot be added to
            container (e.g. already belongs to some fit)
        SlotTakenError -- raised when slot at specified index
            is already taken by other item
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
        """
        Put item to first free slot in container; if
        container doesn't have free slots, append item
        to the end of container.

        Possible exceptions:
        TypeError -- raised when item of unacceptable class
            is passed
        ValueError -- raised when item cannot be added to
            container (e.g. already belongs to some fit)
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
        Remove item or None from container. Also clean container's
        tail if it's filled with Nones. Value can be item, None or
        integer index.

        Possible exceptions:
        ValueError -- if passed item cannot be found in container
        IndexError -- if passed index is out of range of list
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
        # After all the changes, if there're items on the index which
        # we've just cleared and past it, they all changed their positions
        new_positions = {i: self.__list.index(i) for i in self.__list[index:] if i is not None}
        if len(new_positions) > 0:
            self.__fit._publish(InputItemsPositionChanged(new_positions))

    def free(self, value):
        """
        Free item's slot (replace it with None). Also clean
        container's tail if it's filled with Nones. Value can be
        item or integer index.

        Possible exceptions:
        ValueError -- if passed item cannot be found in container
        IndexError -- if passed index is out of range of list
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

    def items(self):
        """Return view over container with just items."""
        return ListItemView(self.__list)

    def clear(self):
        """Remove everything from container."""
        for item in self.__list:
            if item is not None:
                self._handle_item_removal(item)
        self.__list.clear()

    def __getitem__(self, index):
        """Get item by index or items by slice object."""
        return self.__list.__getitem__(index)

    def index(self, value):
        """Get index by item/None."""
        return self.__list.index(value)

    def __iter__(self):
        return self.__list.__iter__()

    def __contains__(self, value):
        return self.__list.__contains__(value)

    def __len__(self):
        return self.__list.__len__()

    def _allocate(self, index):
        """
        If passed index is out of range, complete
        list with Nones until index becomes available.
        """
        allocated_num = len(self.__list)
        self.__list.extend([None] * max(index - allocated_num + 1, 0))

    def _cleanup(self):
        """Remove trailing Nones from list."""
        try:
            while self.__list[-1] is None:
                del self.__list[-1]
        # If we get IndexError, we've ran out of list elements
        # and we're fine with it
        except IndexError:
            pass

    def __repr__(self):
        return repr(self.__list)


class ListItemView:
    """
    Simple class to implement view-like
    functionality over passed list.
    """

    def __init__(self, list_):
        self.__list = list_

    def __iter__(self):
        return (item for item in self.__list if item is not None)

    def __contains__(self, value):
        if value is None:
            return False
        return self.__list.__contains__(value)

    def __len__(self):
        return sum(item is not None for item in self.__list)
