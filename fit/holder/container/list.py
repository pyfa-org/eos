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


from .base import HolderContainerBase


class HolderList(HolderContainerBase):

    def __init__(self, fit, holderClass):
        self.__list = []
        HolderContainerBase.__init__(self, fit, holderClass)

    def __getitem__(self, index):
        return self.__list[index]

    def insert(self, index, thing):
        holder = self.new(thing)
        self._allocate(index - 1)
        self.__list.insert(index, holder)
        self._handleAdd(holder)
        return holder

    def append(self, thing):
        index = len(self.__list)
        return self.insert(index, thing)

    def remove(self, thing):
        if isinstance(thing, int):
            index = thing
            holder = self.__list[index]
        else:
            holder = thing
            index = self.__list.index(holder)
        self._handleRemove(self, holder)
        del self.__list[index]
        self._cleanup()

    def place(self, index, thing):
        try:
            oldHolder = self.__list[index]
        except IndexError:
            pass
        else:
            self._handleRemove(self, oldHolder)
            self.__list[index] = None
        newHolder = self.new(thing)
        self._allocate(index)
        self.__list[index] = newHolder
        self._handleAdd(newHolder)
        return newHolder

    def fill(self, thing):
        try:
            index = self.__list.index(None)
        except ValueError:
            index = len(self.__list)
        return self.place(index, thing)

    def free(self, thing):
        if isinstance(thing, int):
            index = thing
            holder = self.__list[index]
        else:
            holder = thing
            index = self.__list.index(holder)
        self._handleRemove(self, holder)
        self.__list[index] = None
        self._cleanup()

    def index(self, holder):
        return self.__list.index(holder)

    def __iter__(self):
        return iter(self.__list)

    def __contains__(self, holder):
        return holder in self.__list

    def __len__(self):
        return len(self.__list)

    def _allocate(self, index):
        """Fill list with Nones, up to and including specified position."""
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
