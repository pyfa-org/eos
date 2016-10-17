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


class KeyedSet(dict):
    """
    Dictionary-like class, with couple of additional methods which
    make it easier to use it, given that its values are sets with data.
    """

    def add_data_set(self, key, data_set):
        """
        Add data set to dictionary, with proper creation jobs
        if necessary.

        Required arguments:
        key -- key to access dictionary value (data set)
        data_set -- set with data to add to value
        """
        try:
            self[key].update(data_set)
        except KeyError:
            self[key] = set(data_set)

    def rm_data_set(self, key, data_set):
        """
        Remove data set from dictionary, with proper cleanup
        jobs if necessary.

        Required arguments:
        key -- key to access dictionary value (data set)
        data_set -- set with data to remove from value
        """
        try:
            value = self[key]
        except KeyError:
            return
        else:
            value.difference_update(data_set)
            if not value:
                del self[key]

    def add_data(self, key, data):
        """
        Add single object to dictionary, with proper creation
        jobs if necessary.

        Required arguments:
        key -- key to access dictionary value (data set)
        data -- object to add to value
        """
        try:
            self[key].add(data)
        except KeyError:
            self[key] = {data}

    def rm_data(self, key, data):
        """
        Remove single object from dictionary, with proper
        cleanup jobs if necessary.

        Required arguments:
        key -- key to access dictionary value (data set)
        dataSet -- object to remove from value
        """
        try:
            value = self[key]
        except KeyError:
            return
        else:
            value.discard(data)
            if not value:
                del self[key]

    def get_data(self, key):
        """
        Get data set with safe fallback.

        Required arguments:
        key -- key to access dictionary value (data set)

        Return value:
        set with data
        """
        return self.get(key) or set()
