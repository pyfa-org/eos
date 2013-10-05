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


from .set import HolderSet


class HolderRestrictedSet(HolderSet):
    """
    Unordered container for holders, which can't
    contain 2 holders with the same type ID.

    Positional arguments:
    fit -- fit, to which container is attached
    holderClass -- class of holders this container
    is allowed to contain
    """

    __slots__ = ('__typeIdMap')

    def __init__(self, fit, holderClass):
        HolderSet.__init__(self, fit, holderClass)
        self.__typeIdMap = {}

    def add(self, holder):
        """
        Add holder to container.

        Possible exceptions:
        TypeError -- raised when holder of unacceptable class
        is passed
        ValueError -- raised when holder cannot be
        added to container (e.g. already belongs to some fit
        or holder with this type ID exists in container)
        """
        typeId = getattr(holder, '_typeId', None)
        if typeId in self.__typeIdMap:
            msg = 'holder with type ID {} already exists in this set'.format(typeId)
            raise ValueError(msg)
        HolderSet.add(self, holder)
        self.__typeIdMap[typeId] = holder

    def remove(self, holder):
        """
        Remove holder from container.

        Possible exceptions:
        KeyError -- raised when holder cannot be removed
        from container (e.g. it doesn't belong to it)
        """
        HolderSet.remove(self, holder)
        del self.__typeIdMap[holder._typeId]

    def clear(self):
        """Remove everything from container."""
        HolderSet.clear(self)
        self.__typeIdMap.clear()

    def __getitem__(self, typeId):
        """Get holder by type ID"""
        return self.__typeIdMap[typeId]
