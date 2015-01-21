#===============================================================================
# Copyright (C) 2013 Anton Vorobyov
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


import sqlite3
import os.path

from .abc import DataHandler

# SQLite stores bools as 0 or 1, convert them to python bool
sqlite3.register_converter("BOOLEAN", lambda v: int(v) == 1)

class SQLiteDataHandler(DataHandler):

    def __init__(self, dbpath):
        conn = sqlite3.connect(os.path.expanduser(dbpath),
                               detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        self.cursor = conn.cursor()

    def get_invtypes(self):
        return self.__fetch_table('invtypes')

    def get_invgroups(self):
        return self.__fetch_table('invgroups')

    def get_dgmattribs(self):
        return self.__fetch_table('dgmattribs')

    def get_dgmtypeattribs(self):
        return self.__fetch_table('dgmtypeattribs')

    def get_dgmeffects(self):
        return self.__fetch_table('dgmeffects')

    def get_dgmtypeeffects(self):
        return self.__fetch_table('dgmtypeeffects')

    def get_dgmexpressions(self):
        return self.__fetch_table('dgmexpressions')

    def __fetch_table(self, tablename):
        self.cursor.execute("SELECT * FROM {}".format(tablename))
        rows = []
        for row in self.cursor:
            rows.append(dict(row))
        return rows

    def get_version(self):
        metadata = self.__fetch_table('metadata')
        # If we won't find version field, it will be None
        version = None
        for row in metadata:
            if row['field_name'] == 'client_build':
                version = row['field_value']
                break
        return version
