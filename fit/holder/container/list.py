#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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
#===============================================================================


from eos.fit.exception import HolderAddError
from .base import HolderContainerBase
from .exception import SlotTakenError


class HolderList(HolderContainerBase):
    """
    Ordered container for holders.

    Positional arguments:
    fit -- fit, to which container is attached
    """

    __slots__ = ('__list')

    def __init__(self, fit):
        self.__list = []
        HolderContainerBase.__init__(self, fit)

    def insert(self, index, value):
        """
        Insert value to given position; if position is
        out of range of container and value is holder,
        fill container with Nones up to position and
        put holder there. Also value can be None to
        insert empty slots between holders.

        Possible exceptions:
        ValueError -- raised when holder is passed as value and
        it cannot be added to container (e.g. already belongs to
        some fit)
        """
        self._allocate(index - 1)
        self.__list.insert(index, value)
        if value is None:
            self._cleanup()
        else:
            try:
                self._handleAdd(value)
            except HolderAddError as e:
                del self.__list[index]
                self._cleanup()
                raise ValueError(value) from e

    def append(self, holder):
        """
        Append holder to the end of container.

        Possible exceptions:
        ValueError -- raised when holder cannot be
        added to container (e.g. already belongs to some fit)
        """
        self.__list.append(holder)
        try:
            self._handleAdd(holder)
        except HolderAddError as e:
            del self.__list[-1]
            raise ValueError(holder) from e

    def place(self, index, holder):
        """
        Put holder to given position; if position is out of
        range of container, fill it with Nones up to position
        and put holder there.

        Possible exceptions:
        ValueError -- raised when holder cannot be added to
        container (e.g. already belongs to some fit)
        SlotTakenError -- raised when slot at specified index
        is already taken by other holder
        """
        try:
            oldHolder = self.__list[index]
        except IndexError:
            self._allocate(index)
        else:
            if oldHolder is not None:
                raise SlotTakenError(index)
        self.__list[index] = holder
        try:
            self._handleAdd(holder)
        except HolderAddError as e:
            self.__list[index] = None
            self._cleanup()
            raise ValueError(holder) from e

    def equip(self, holder):
        """
        Put holder to first free slot in container; if
        container doesn't have free slots, append holder
        to the end of container.

        Possible exceptions:
        ValueError -- raised when holder cannot be added to
        container (e.g. already belongs to some fit)
        """
        try:
            index = self.__list.index(None)
        except ValueError:
            index = len(self.__list)
            self.__list.append(holder)
        else:
            self.__list[index] = holder
        try:
            self._handleAdd(holder)
        except HolderAddError as e:
            self.__list[index] = None
            self._cleanup()
            raise ValueError(holder) from e

    def remove(self, value):
        """
        Remove holder or None from container. Also clean container's
        tail if it's filled with Nones. Value can be holder, None or
        integer index.

        Possible exceptions:
        ValueError -- if passed holder cannot be found in container
        IndexError -- if passed index is out of range of list
        """
        if isinstance(value, int):
            index = value
            holder = self.__list[index]
        else:
            holder = value
            index = self.__list.index(holder)
        if holder is not None:
            self._handleRemove(holder)
        del self.__list[index]
        self._cleanup()

    def free(self, value):
        """
        Free holder's slot (replace it with None). Also clean
        container's tail if it's filled with Nones. Value can be
        holder or integer index.

        Possible exceptions:
        ValueError -- if passed holder cannot be found in container
        IndexError -- if passed index is out of range of list
        """
        if isinstance(value, int):
            index = value
            holder = self.__list[index]
            if holder is None:
                return
        else:
            holder = value
            index = self.__list.index(holder)
        self._handleRemove(holder)
        self.__list[index] = None
        self._cleanup()

    def holders(self):
        """Return view over container with just holders."""
        return HolderView(self.__list)

    def clear(self):
        """Remove everything from container."""
        for holder in self.__list:
            if holder is not None:
                self._handleRemove(holder)
        self.__list.clear()

    def __getitem__(self, index):
        """Get holder by index."""
        return self.__list[index]

    def index(self, holder):
        """Get index by holder."""
        return self.__list.index(holder)

    def __iter__(self):
        return iter(self.__list)

    def __contains__(self, holder):
        return holder in self.__list

    def __len__(self):
        return len(self.__list)

    def _allocate(self, index):
        """
        If passed index is out of range, complete
        list with Nones until index becomes available.
        """
        allocatedNum = len(self.__list)
        for _ in range(max(index - allocatedNum + 1, 0)):
            self.__list.append(None)

    def _cleanup(self):
        """Remove trailing Nones from list."""
        try:
            while self.__list[-1] is None:
                del self.__list[-1]
        # If we get IndexError, we've ran out of list elements
        # and we're fine with it
        except IndexError:
            pass


class HolderView:
    """
    Simple class to implement view-like
    functionality over passed list.
    """

    __slots__ = ('__list')

    def __init__(self, list_):
        self.__list = list_

    def __iter__(self):
        return (item for item in self.__list if item is not None)

    def __len__(self):
        return sum(item is not None for item in self.__list)
