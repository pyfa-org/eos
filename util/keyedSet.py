#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2012 Anton Vorobyov
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


class KeyedSet(dict):
    """
    Dictionary-like class, with couple of additional methods which
    make it easier to use it, given that its values are sets with data.
    """

    def addData(self, key, data):
        """
        Add data set to dictionary, with proper creation jobs
        if necessary.

        Positional arguments:
        key -- key to access dictionary value (data set)
        data -- set with data to add to value
        """
        try:
            value = self[key]
        except KeyError:
            value = self[key] = set()
        value.update(data)

    def rmData(self, key, data):
        """
        Remove data set from dictionary, with proper cleanup
        jobs if necessary.

        Positional arguments:
        key -- key to access dictionary value (data set)
        data -- set with data to remove from value
        """
        try:
            value = self[key]
        except KeyError:
            return
        else:
            value.difference_update(data)
            if len(value) == 0:
                del self[key]

    def getData(self, key):
        """
        Get data set with safe fallback.

        Positional arguments:
        key -- key to access dictionary value (data set)

        Return value:
        set with data
        """
        data = self.get(key, set())
        return data
