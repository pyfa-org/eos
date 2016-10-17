# ===============================================================================
# Copyright (C) 2013-2015 Anton Vorobyov
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


import sqlite3

from eos.util.repr import make_repr_str
from .abc import BaseDataHandler


# SQLite stores bools as 0 or 1, convert them to python bool
sqlite3.register_converter('BOOLEAN', lambda v: int(v) == 1)


class SQLiteDataHandler(BaseDataHandler):
    """
    Handler for loading data from SQLite database. Data should be in Phobos-like
    format, for details on it refer to JSON data handler doc string.
    """

    def __init__(self, dbpath):
        conn = sqlite3.connect(dbpath, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        self.cursor = conn.cursor()

    def get_evetypes(self):
        return self.__fetch_table('evetypes')

    def get_evegroups(self):
        return self.__fetch_table('evegroups')

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
        self.cursor.execute('SELECT * FROM {}'.format(tablename))
        return [dict(row) for row in self.cursor]

    def get_version(self):
        self.cursor.execute('SELECT field_value FROM phbmetadata WHERE field_name = "client_build"')
        for row in self.cursor:
            return row[0]
        else:
            return None

    def __repr__(self):
        return make_repr_str(self, ())
