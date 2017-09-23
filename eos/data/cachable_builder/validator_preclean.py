# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2017 Anton Vorobyov
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


from logging import getLogger
from numbers import Integral


logger = getLogger(__name__)


class ValidatorPreCleanup:

    @staticmethod
    def run(data):
        """
        Run checks which should be performed on
        data which is yet to be cleaned.

        Required arguments:
        data -- data to check
        """
        primary_keys = {
            'dgmattribs': ('attributeID',),
            'dgmeffects': ('effectID',),
            'dgmexpressions': ('expressionID',),
            'dgmtypeattribs': ('typeID', 'attributeID'),
            'dgmtypeeffects': ('typeID', 'effectID'),
            'evegroups': ('groupID',),
            'evetypes': ('typeID',),
            'typefighterabils': ('typeID', 'abilityID')
        }
        for table_name, key_names in primary_keys.items():
            ValidatorPreCleanup._table_pk(data[table_name], table_name, key_names)

    @staticmethod
    def _table_pk(table, table_name, key_names):
        """
        Check if all primary keys in table are integers.

        Required arguments:
        table_name -- name of table to check
        key_names -- names of fields which are considerred
            as primary keys in iterable
        """
        # Contains keys used in current table
        used_keys = set()
        # Storage for rows which should be removed
        invalid_rows = set()
        for datarow in sorted(table, key=lambda row: row['table_pos']):
            ValidatorPreCleanup._row_pk(key_names, datarow, used_keys, invalid_rows)
        # If any invalid rows were detected, remove them and
        # write corresponding message to log
        if invalid_rows:
            msg = '{} rows in table {} have invalid PKs, removing them'.format(
                len(invalid_rows), table_name)
            logger.warning(msg)
            table.difference_update(invalid_rows)

    @staticmethod
    def _row_pk(key_names, datarow, used_keys, invalid_rows):
        """
        Check row primary key for validity.

        Required arguments:
        key_names -- names of fields which contain keys
        datarow -- row to check
        used_keys -- container with already used keys
        invalid_rows -- container for invalid rows
        """
        row_key = []
        for key_name in key_names:
            try:
                key_value = datarow[key_name]
            # Invalidate row if it doesn't have any component
            # of primary key
            except KeyError:
                invalid_rows.add(datarow)
                return
            # If primary key is not an integer
            if not isinstance(key_value, Integral):
                invalid_rows.add(datarow)
                return
            row_key.append(key_value)
        row_key = tuple(row_key)
        # If specified key is already used
        if row_key in used_keys:
            invalid_rows.add(datarow)
            return
        used_keys.add(row_key)
