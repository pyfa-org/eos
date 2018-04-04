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


class KeyedStorage(dict):
    """Container for data sets with keyed access.

    Access to sets in container is provided only via keys. In other words,
    regular dictionary with values being sets.
    """

    def add_data_set(self, key, data_set):
        """Add data set.

        If set accessed by passed key doesn't exist, create it.

        Args:
            key: Defines into which set we should add new data.
            data_set: Iterable with data to add.
        """
        try:
            self[key].update(data_set)
        except KeyError:
            self[key] = set(data_set)

    def rm_data_set(self, key, data_set):
        """Remove data set.

        If requested data doesn't exit in target set, silently ignore it, remove
        only stuff which is stored. If after removal set contains no data, run
        cleanup jobs.

        Args:
            key: Defines from which set we should remove data.
            data_set: Iterable with data to remove.
        """
        try:
            value = self[key]
        except KeyError:
            return
        else:
            value.difference_update(data_set)
            if not value:
                del self[key]

    def add_data_entry(self, key, data):
        """Add data entry.

        If set accessed by passed key doesn't exist, create it.

        Args:
            key: Defines into which set we should add new data.
            data: Single data entry to add.
        """
        try:
            self[key].add(data)
        except KeyError:
            self[key] = {data}

    def rm_data_entry(self, key, data):
        """Remove data entry.

        If requested data doesn't exit in target set, silently ignore it, remove
        only stuff which is stored. If after removal set contains no data, run
        cleanup jobs.

        Args:
            key: Defines from which set we should remove data.
            data: Single data entry to remove.
        """
        try:
            value = self[key]
        except KeyError:
            return
        else:
            value.discard(data)
            if not value:
                del self[key]
