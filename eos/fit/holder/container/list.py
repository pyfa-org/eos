# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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


from eos.fit.exception import HolderAlreadyAssignedError
from .base import HolderContainerBase
from .exception import SlotTakenError


class HolderList(HolderContainerBase):
    """
    Ordered container for holders.

    Required arguments:
    fit -- fit, to which container is attached
    holder_class -- class of holders this container
    is allowed to contain
    """

    def __init__(self, fit, holder_class):
        super().__init__(holder_class)
        self.__fit = fit
        self.__list = []

    def insert(self, index, value):
        """
        Insert value to given position; if position is
        out of range of container and value is holder,
        fill container with Nones up to position and
        put holder there. Also value can be None to
        insert empty slots between holders.

        Possible exceptions:
        TypeError -- raised when holder of unacceptable class
        is passed
        ValueError -- raised when holder is passed as value and
        it cannot be added to container (e.g. already belongs to
        some fit)
        """
        self._check_class(value, allow_none=True)
        self._allocate(index - 1)
        self.__list.insert(index, value)
        if value is None:
            self._cleanup()
        else:
            try:
                self.__fit._add_holder(value)
            except HolderAlreadyAssignedError as e:
                del self.__list[index]
                self._cleanup()
                raise ValueError(*e.args) from e
        self.__fit._request_volatile_cleanup()

    def append(self, holder):
        """
        Append holder to the end of container.

        Possible exceptions:
        TypeError -- raised when holder of unacceptable class
        is passed
        ValueError -- raised when holder cannot be
        added to container (e.g. already belongs to some fit)
        """
        self._check_class(holder)
        self.__list.append(holder)
        try:
            self.__fit._add_holder(holder)
        except HolderAlreadyAssignedError as e:
            del self.__list[-1]
            raise ValueError(*e.args) from e
        self.__fit._request_volatile_cleanup()

    def place(self, index, holder):
        """
        Put holder to given position; if position is out of
        range of container, fill it with Nones up to position
        and put holder there.

        Possible exceptions:
        TypeError -- raised when holder of unacceptable class
        is passed
        ValueError -- raised when holder cannot be added to
        container (e.g. already belongs to some fit)
        SlotTakenError -- raised when slot at specified index
        is already taken by other holder
        """
        self._check_class(holder)
        try:
            old_holder = self.__list[index]
        except IndexError:
            self._allocate(index)
        else:
            if old_holder is not None:
                raise SlotTakenError(index)
        self.__list[index] = holder
        try:
            self.__fit._add_holder(holder)
        except HolderAlreadyAssignedError as e:
            self.__list[index] = None
            self._cleanup()
            raise ValueError(*e.args) from e
        self.__fit._request_volatile_cleanup()

    def equip(self, holder):
        """
        Put holder to first free slot in container; if
        container doesn't have free slots, append holder
        to the end of container.

        Possible exceptions:
        TypeError -- raised when holder of unacceptable class
        is passed
        ValueError -- raised when holder cannot be added to
        container (e.g. already belongs to some fit)
        """
        self._check_class(holder)
        try:
            index = self.__list.index(None)
        except ValueError:
            index = len(self.__list)
            self.__list.append(holder)
        else:
            self.__list[index] = holder
        try:
            self.__fit._add_holder(holder)
        except HolderAlreadyAssignedError as e:
            self.__list[index] = None
            self._cleanup()
            raise ValueError(*e.args) from e
        self.__fit._request_volatile_cleanup()

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
        self.__fit._request_volatile_cleanup()
        if holder is not None:
            self.__fit._remove_holder(holder)
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
        else:
            holder = value
            index = self.__list.index(holder)
        if holder is None:
            return
        self.__fit._request_volatile_cleanup()
        self.__fit._remove_holder(holder)
        self.__list[index] = None
        self._cleanup()

    def holders(self):
        """Return view over container with just holders."""
        return ListHolderView(self.__list)

    def clear(self):
        """Remove everything from container."""
        self.__fit._request_volatile_cleanup()
        for holder in self.__list:
            if holder is not None:
                self.__fit._remove_holder(holder)
        self.__list.clear()

    def __getitem__(self, index):
        """Get holder by index or holders by slice object."""
        return self.__list.__getitem__(index)

    def index(self, value):
        """Get index by holder/None."""
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
        for _ in range(max(index - allocated_num + 1, 0)):
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

    def __repr__(self):
        return repr(self.__list)


class ListHolderView:
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
