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
from numbers import Real

from eos.const.eve import Effect
from eos.util.frozen_dict import FrozenDict


logger = getLogger(__name__)


class ValidatorPreConversion:

    @staticmethod
    def run(data):
        """
        As data convertor and eos relies on some
        assumptions, check that data corresponds to them.

        Required arguments:
        data -- data to check
        """
        ValidatorPreConversion._attribute_value_type(data)
        ValidatorPreConversion._multiple_default_effects(data)
        ValidatorPreConversion._colliding_module_racks(data)

    @staticmethod
    def _attribute_value_type(data):
        """
        Check all attributes of all items for validity.
        Only ints and floats are considered as valid. Eos
        attribute calculation engine relies on this assumption.
        """
        invalid_rows = set()
        table = data['dgmtypeattribs']
        for row in table:
            if not isinstance(row.get('value'), Real):
                invalid_rows.add(row)
        if invalid_rows:
            msg = '{} attribute rows have non-numeric value, removing them'.format(
                len(invalid_rows))
            logger.warning(msg)
            table.difference_update(invalid_rows)

    @staticmethod
    def _multiple_default_effects(data):
        """
        Each type must have one default effect at max. Data
        conversion relies on this assumption.
        """
        # Set with IDs of types, which have default effect
        defeff = set()
        table = data['dgmtypeeffects']
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

    @staticmethod
    def _colliding_module_racks(data):
        """
        Type of slot into which module is placed is detected
        using module's effects. Engine relies on assumption that
        each module has at max one such effect. This type of check
        is better to be performed after data cleanup, because slot
        type effects are still used on many item types we do not need
        and want to remove to avoid printing unnecessary log entries.
        """
        table = data['dgmtypeeffects']
        rack_effects = (Effect.hi_power, Effect.med_power, Effect.lo_power)
        racked_items = set()
        invalid_rows = set()
        for row in sorted(table, key=lambda r: r['table_pos']):
            effect_id = row['effectID']
            # We're not interested in anything besides
            # rack effects
            if effect_id not in rack_effects:
                continue
            eve_type_id = row['typeID']
            if eve_type_id in racked_items:
                invalid_rows.add(row)
            else:
                racked_items.add(eve_type_id)
        if invalid_rows:
            msg = '{} rows contain colliding module racks, removing them'.format(
                len(invalid_rows))
            logger.warning(msg)
            table.difference_update(invalid_rows)
