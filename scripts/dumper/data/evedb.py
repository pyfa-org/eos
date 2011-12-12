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

from data.dictlist import DictList
from data.table import Table

class EveDB(DictList):
    """
    Class-container for multiple tables
    """
    def __init__(self):
        DictList.__init__(self)

    def add_table(self, name):
        """Add table to container"""
        new_table = Table(name)
        try:
            self.append(new_table)
        except ValueError:
            raise ValueError("table with name {0} already exists".format(new_table.name))
        return new_table
