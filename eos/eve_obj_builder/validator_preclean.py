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


from logging import getLogger
from numbers import Integral


logger = getLogger(__name__)


class ValidatorPreClean:

    @classmethod
    def run(cls, data):
        """Verify data before cleanup.

        Cleanup process relies on data consistency. Here, we make sure that it's
        consistent enough. We do not try too hard, and other inconsistencies
        will be removed after cleanup.

        Args:
            data: Dictionary in {table name: {table, rows}} format.
        """
        # Format: {table name: (primary, keys)}
        pk_spec = {
            'dgmattribs': ['attributeID'],
            'dgmeffects': ['effectID'],
            'dgmtypeattribs': ['typeID', 'attributeID'],
            'dgmtypeeffects': ['typeID', 'effectID'],
            'evegroups': ['groupID'],
            'evetypes': ['typeID'],
            'dbuffcollections': ['buffID'],
            'skillreqs': ['typeID', 'skillTypeID'],
            'typefighterabils': ['typeID', 'abilityID']}
        for table_name, pks in pk_spec.items():
            cls._table_pk(pks, data[table_name], table_name)

    @classmethod
    def _table_pk(cls, pks, rows, table_name):
        """Check if all primary keys in table are integers.

        Args:
            pks: Iterable with PK names.
            rows: Iterable with table data rows.
            table_name: Table name, used just for logging.
        """
        # Contains primary keys used in current table
        seen_pks = set()
        # Storage for rows which should be removed
        invalid_rows = set()
        for row in sorted(rows, key=lambda row: row['table_pos']):
            cls._row_pk(pks, row, seen_pks, invalid_rows)
        # If any invalid rows were detected, remove them and write corresponding
        # message to log
        if invalid_rows:
            msg = '{} rows in table {} have invalid PKs, removing them'.format(
                len(invalid_rows), table_name)
            logger.warning(msg)
            rows.difference_update(invalid_rows)

    @staticmethod
    def _row_pk(pks, row, seen_pks, invalid_rows):
        """Check row PK for validity.

        If PK is invalid, that is, has already been seen before, add row to
        invalid rows container.

        Args:
            pks: Iterable with PK names.
            row: Data row which we should check.
            seen_pks: Iterable with PKs which we already seen when iterating
                over current table.
            invalid_rows: Container for invalid rows.
        """
        row_pk = []
        for pk_name in pks:
            try:
                pk_value = row[pk_name]
            # Invalidate row if it doesn't have any component of primary key
            except KeyError:
                invalid_rows.add(row)
                return
            if not isinstance(pk_value, Integral):
                invalid_rows.add(row)
                return
            row_pk.append(pk_value)
        row_pk = tuple(row_pk)
        if row_pk in seen_pks:
            invalid_rows.add(row)
            return
        seen_pks.add(row_pk)
