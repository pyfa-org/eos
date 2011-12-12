#===============================================================================
# Copyright (C) 2010-2011 Anton Vorobyov
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

from data.column import Column
from data.dictlist import DictList

class Table(DictList):
    """
    Class-container for table data, plus several auxiliary methods
    """
    def __init__(self, name):
        DictList.__init__(self)
        self.name = name
        self.datarows = set()

    def add_column(self, name):
        """Add column to table"""
        if len(self.datarows) > 0:
            raise RuntimeError("attempt to add column to table with data detected")
        new_column = Column(name)
        try:
            self.append(new_column)
        except ValueError:
            raise ValueError("column with name {0} already exists".format(new_column.name))
        return new_column

    def remove(self, column):
        """Avoid accessing remove method of underlying class directly"""
        self.remove_columns({column.name})
        return

    def remove_columns(self, colnames):
        """Remove columns and all associated data"""
        # Problems flag
        problems = False
        # Gather list of columns to be removed and indices of
        # columns to be kept
        cols2remove = []
        indices2keep = []
        for column in self:
            # We don't want to remove PKs, inform about it
            if column.name in colnames and column.pk is True:
                print("  Primary key {0} of table {1} forcibly passes filter".format(column.name, self.name))
                # And set error flag
                problems = True
            if column.name in colnames and column.pk is not True:
                cols2remove.append(column)
            else:
                indices2keep.append(self.index(column))
        # Remove column objects from list
        for column in cols2remove:
            DictList.remove(self, column)
        # Compose new set of data
        newrows = set()
        for datarow in self.datarows:
            newrow = tuple(datarow[i] for i in indices2keep)
            newrows.add(newrow)
        # Replace old set with new one
        self.datarows = newrows
        # Return error flag
        return problems

    def index_byname(self, name):
        """Return index of column with given name"""
        column = self[name]
        idx = self.index(column)
        return idx

    def is_duplicate(self, other):
        """Compare two tables and report if they're duplicates"""
        # Do not consider self as duplicate
        if self is other:
            return False
        # Check column names
        if tuple(c.name for c in self) != tuple(c.name for c in other):
            return False
        # Tables with no columns also are not considered as duplicates
        if len(self) == 0 and len(other) == 0:
            return False
        # Check all data
        if self.datarows != other.datarows:
            return False
        return True

    def get_pks(self):
        """Get tuple with primary keys of table"""
        pks = tuple(filter(lambda col: col.pk is True, self))
        return pks

    def get_fks(self):
        """Get tuple with foreign keys of table"""
        fks = tuple(filter(lambda col: col.fk is not None, self))
        return fks

    def get_indices(self):
        """Get tuple with indexed columns of table"""
        indices = tuple(filter(lambda col: col.index is True, self))
        return indices

    def get_columndataset(self, name):
        """Get all data from certain column into set"""
        idx = self.index(self[name])
        dataset = set(dr[idx] for dr in self.datarows)
        return dataset
