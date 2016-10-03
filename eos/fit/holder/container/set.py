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


class HolderSet(HolderContainerBase):
    """
    Unordered container for holders.

    Required arguments:
    fit -- fit, to which container is attached
    holder_class -- class of holders this container
    is allowed to contain
    """

    def __init__(self, fit, holder_class):
        super().__init__(holder_class)
        self.__fit = fit
        self.__set = set()

    def add(self, holder):
        """
        Add holder to container.

        Possible exceptions:
        TypeError -- raised when holder of unacceptable class
        is passed
        ValueError -- raised when holder cannot be
        added to container (e.g. already belongs to some fit)
        """
        self._check_class(holder)
        self.__set.add(holder)
        try:
            self.__fit._add_holder(holder)
        except HolderAlreadyAssignedError as e:
            self.__set.remove(holder)
            raise ValueError(*e.args) from e
        self.__fit._request_volatile_cleanup()

    def remove(self, holder):
        """
        Remove holder from container.

        Possible exceptions:
        KeyError -- raised when holder cannot be removed
        from container (e.g. it doesn't belong to it)
        """
        if holder not in self.__set:
            raise KeyError(holder)
        self.__fit._request_volatile_cleanup()
        self.__fit._remove_holder(holder)
        self.__set.remove(holder)

    def clear(self):
        """Remove everything from container."""
        self.__fit._request_volatile_cleanup()
        for holder in self.__set:
            self.__fit._remove_holder(holder)
        self.__set.clear()

    def __iter__(self):
        return self.__set.__iter__()

    def __contains__(self, holder):
        return self.__set.__contains__(holder)

    def __len__(self):
        return self.__set.__len__()

    def __repr__(self):
        return repr(self.__set)
