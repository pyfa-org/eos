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


from logging import getLogger

from eos.const.eve import Effect
from eos.util.frozen_dict import FrozenDict


logger = getLogger(__name__)


class Checker:
    """
    Class responsible for conducting checks and making
    data consistent for further stages of processing.
    """

    def pre_cleanup(self, data):
        """
        Run checks which should be performed on
        data which is yet to be cleaned.

        Required arguments:
        data -- data to check
        """
        self.data = data
        primary_keys = {
            'dgmattribs': ('attributeID',),
            'dgmeffects': ('effectID',),
            'dgmexpressions': ('expressionID',),
            'dgmtypeattribs': ('typeID', 'attributeID'),
            'dgmtypeeffects': ('typeID', 'effectID'),
            'evegroups': ('groupID',),
            'evetypes': ('typeID',)
        }
        for table_name, key_names in primary_keys.items():
            self._table_pk(table_name, key_names)

    def pre_convert(self, data):
        """
        As data convertor and eos relies on some
        assumptions, check that data corresponds to them.

        Required arguments:
        data -- data to check
        """
        self.data = data
        self._attribute_value_type()
        self._multiple_default_effects()
        self._colliding_module_racks()

    def _table_pk(self, table_name, key_names):
        """
        Check if all primary keys in table are integers.

        Required arguments:
        table_name -- name of table to check
        key_names -- names of fields which are considerred
        as primary keys in iterable
        """
        table = self.data[table_name]
        # Contains keys used in current table
        used_keys = set()
        # Storage for rows which should be removed
        invalid_rows = set()
        for datarow in sorted(table, key=lambda row: row['table_pos']):
            self._row_pk(key_names, datarow, used_keys, invalid_rows)
        # If any invalid rows were detected, remove them and
        # write corresponding message to log
        if invalid_rows:
            msg = '{} rows in table {} have invalid PKs, removing them'.format(
                len(invalid_rows), table_name)
            logger.warning(msg)
            table.difference_update(invalid_rows)

    def _row_pk(self, key_names, datarow, used_keys, invalid_rows):
        """
        Check row primary key for validity.

        Required arguments:
        key_names -- names of fields which contain keys
        datarow -- row to check
        used_keys -- container with alreaady used keys
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
            if not isinstance(key_value, int):
                invalid_rows.add(datarow)
                return
            row_key.append(key_value)
        row_key = tuple(row_key)
        # If specified key is already used
        if row_key in used_keys:
            invalid_rows.add(datarow)
            return
        used_keys.add(row_key)

    def _attribute_value_type(self):
        """
        Check all attributes of all items for validity.
        Only ints and floats are considered as valid. Eos
        attribute calculation engine relies on this assumption.
        """
        invalid_rows = set()
        table = self.data['dgmtypeattribs']
        for row in table:
            if not isinstance(row.get('value'), (int, float)):
                invalid_rows.add(row)
        if invalid_rows:
            msg = '{} attribute rows have non-numeric value, removing them'.format(
                len(invalid_rows))
            logger.warning(msg)
            table.difference_update(invalid_rows)

    def _multiple_default_effects(self):
        """
        Each type must have one default effect at max. Data
        conversion (and resulting data structure) relies on
        this assumption.
        """
        # Set with IDs of types, which have default effect
        defeff = set()
        table = self.data['dgmtypeeffects']
        invalid_rows = set()
        for row in sorted(table, key=lambda r: r['table_pos']):
            is_default = row.get('isDefault')
            # We're interested only in default effects
            if is_default is not True:
                continue
            type_id = row['typeID']
            # If we already saw default effect for given type ID,
            # invalidate current row
            if type_id in defeff:
                invalid_rows.add(row)
            else:
                defeff.add(type_id)
        # Process ivalid rows, if any
        if invalid_rows:
            msg = 'data contains {} excessive default effects, marking them as non-default'.format(
                len(invalid_rows))
            logger.warning(msg)
            # Replace isDefault field value with False for invalid rows
            table.difference_update(invalid_rows)
            for invalid_row in invalid_rows:
                new_row = {}
                for field, value in invalid_row.items():
                    new_row[field] = False if field == 'isDefault' else value
                table.add(FrozenDict(new_row))

    def _colliding_module_racks(self):
        """
        Type of slot into which module is placed is detected
        using module's effects. Engine relies on assumption that
        each module has at max one such effect. This type of check
        is better to be performed after data cleanup, because slot
        type effects are still used on many other items (and thus
        are not needed to be removed), and errors for items which
        won't be actually used won't be printed.
        """
        table = self.data['dgmtypeeffects']
        rack_effects = (Effect.hi_power, Effect.med_power, Effect.lo_power)
        racked_items = set()
        invalid_rows = set()
        for row in sorted(table, key=lambda r: r['table_pos']):
            effect_id = row['effectID']
            # We're not interested in anything besides
            # rack effects
            if effect_id not in rack_effects:
                continue
            type_id = row['typeID']
            if type_id in racked_items:
                invalid_rows.add(row)
            else:
                racked_items.add(type_id)
        if invalid_rows:
            msg = '{} rows contain colliding module racks, removing them'.format(
                len(invalid_rows))
            logger.warning(msg)
            table.difference_update(invalid_rows)
