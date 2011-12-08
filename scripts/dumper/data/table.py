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

from data import Column

class Table(object):
    """
    Class-container for table data, plus several auxiliary methods
    """
    def __init__(self, name):
        self.name = name
        self.columns = []
        self.datarows = set()

    def addcolumn(self, name):
        """Add column to table"""
        existing = self.getcolumn(name)
        if existing is None:
            self.columns.append(Column(name))
        else:
            raise ValueError("column with name {0} already exists".format(name))

    def getcolumn(self, name):
        """Get column with requested name"""
        for column in self.columns:
            if column.name == name:
                return column
        return None

    def removecolumns(self, colnames):
        """Remove columns and all associated data"""
        # Problems flag
        problems = False
        # Gather list of columns to be removed and indices of
        # columns to be kept
        colstoremove = []
        indicestokeep = []
        for column in self.columns:
            # We don't want to remove PKs, inform about it
            if column.name in colnames and column.pk is True:
                print("  Primary key {0} of table {1} forcibly passes filter".format(column.name, self.name))
                # And set error flag
                problems = True
            # And actually make sure we don't remove it
            if column.name in colnames and column.pk is not True:
                colstoremove.append(column)
            else:
                indicestokeep.append(self.columns.index(column))
        # Remove column objects from list
        for col in colstoremove:
            self.columns.remove(col)
        # Compose new set of data
        newrows = set()
        for datarow in self.datarows:
            newrow = tuple(datarow[i] for i in indicestokeep)
            newrows.add(newrow)
        # Replace old set with new one
        self.datarows = newrows
        # Return error flag
        return problems

    def getcolumnidx(self, name):
        """Get index of column with passed name in given table"""
        idx = self.columns.index(self.getcolumn(name))
        return idx

    def isduplicate(self, other):
        """Compare two tables and report if they're duplicates"""
        # Do not consider self as duplicate
        if self == other:
            return False
        # Check column names
        if tuple(c.name for c in self.columns) != tuple(c.name for c in other.columns):
            return False
        # Tables with no columns also are not considered as duplicates
        if len(self.columns) == 0 and len(other.columns) == 0:
            return False
        # Check all data
        if self.datarows != other.datarows:
            return False
        return True

    def getpks(self):
        """Get tuple with primary keys of table"""
        pks = tuple(filter(lambda col: col.pk is True, self.columns))
        return pks

    def getfks(self):
        """Get tuple with foreign keys of table"""
        fks = tuple(filter(lambda col: col.fk is not None, self.columns))
        return fks

    def getindices(self):
        """Get tuple with indexed columns of table"""
        indices = tuple(filter(lambda col: col.index is True, self.columns))
        return indices

    def getcolumndataset(self, name):
        """Get all data from certain column into set"""
        idx = self.getcolumnidx(name)
        dataset = set(dr[idx] for dr in self.datarows)
        # Remove None value from set, if it's there
        dataset.difference_update({None})
        return dataset
