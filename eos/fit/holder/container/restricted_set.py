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


from .set import HolderSet


class HolderRestrictedSet(HolderSet):
    """
    Unordered container for holders, which can't
    contain 2 holders with the same type ID.

    Required arguments:
    fit -- fit, to which container is attached
    holder_class -- class of holders this container
    is allowed to contain
    """

    def __init__(self, fit, holder_class):
        super().__init__(fit, holder_class)
        self.__type_id_map = {}

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
        type_id = getattr(holder, '_type_id', None)
        if type_id in self.__type_id_map:
            msg = 'holder with type ID {} already exists in this set'.format(type_id)
            raise ValueError(msg)
        super().add(holder)
        self.__type_id_map[type_id] = holder

    def remove(self, holder):
        """
        Remove holder from container.

        Possible exceptions:
        KeyError -- raised when holder cannot be removed
        from container (e.g. it doesn't belong to it)
        """
        super().remove(holder)
        del self.__type_id_map[holder._type_id]

    def clear(self):
        """Remove everything from container."""
        super().clear()
        self.__type_id_map.clear()

    def __getitem__(self, type_id):
        """Get holder by type ID"""
        return self.__type_id_map[type_id]

    def __delitem__(self, type_id):
        """Remove holder by type ID"""
        holder = self.__type_id_map[type_id]
        self.remove(holder)
