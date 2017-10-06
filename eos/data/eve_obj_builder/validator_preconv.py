# ==============================================================================
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
# ==============================================================================


from logging import getLogger
from numbers import Real

from eos.const.eve import EffectId
from eos.util.frozen_dict import FrozenDict


logger = getLogger(__name__)


class ValidatorPreConv:

    @staticmethod
    def run(data):
        """Verify data before conversion.

        Conversion of data into Eos-specific eve objects relies on several
        assumptions about the data. Here, we make sure that these assumptions
        are correct.

        Args:
            data: Dictionary in {table name: {table, rows}} format.
        """
        ValidatorPreConv._attribute_value_type(data['dgmtypeattribs'])
        ValidatorPreConv._multiple_default_effects(data['dgmtypeeffects'])
        ValidatorPreConv._colliding_module_racks(data['dgmtypeeffects'])

    @staticmethod
    def _attribute_value_type(dta_rows):
        """Make sure that all attributes have numeric values.

        Args:
            dta_rows: Iterable with data rows from dgmtypeattribs table.
        """
        invalid_rows = set()
        for row in dta_rows:
            if not isinstance(row.get('value'), Real):
                invalid_rows.add(row)
        if invalid_rows:
            msg = (
                '{} attribute rows have non-numeric value, removing them'
            ).format(len(invalid_rows))
            logger.warning(msg)
            dta_rows.difference_update(invalid_rows)

    @staticmethod
    def _multiple_default_effects(dte_rows):
        """Check that each type has one default effect maximum.

        Args:
            dte_rows: Iterable with data rows from dgmtypeeffects table.
        """
        # Set with IDs of eve types, which have default effect
        defeff = set()
        invalid_rows = set()
        for row in sorted(dte_rows, key=lambda r: r['table_pos']):
            is_default = row.get('isDefault')
            # We're interested only in default effects
            if not is_default:
                continue
            type_id = row['typeID']
            # If we already saw default effect for given type ID, invalidate
            # current row
            if type_id in defeff:
                invalid_rows.add(row)
            else:
                defeff.add(type_id)
        if invalid_rows:
            msg = (
                'data contains {} excessive default effects, '
                'marking them as non-default'
            ).format(len(invalid_rows))
            logger.warning(msg)
            # Replace isDefault field value with False for invalid rows
            dte_rows.difference_update(invalid_rows)
            for invalid_row in invalid_rows:
                new_row = {}
                for field, value in invalid_row.items():
                    new_row[field] = False if field == 'isDefault' else value
                dte_rows.add(FrozenDict(new_row))

    @staticmethod
    def _colliding_module_racks(dte_rows):
        """Check that items can be assigned into one module rack maximum.

        Type of slot into which module is placed is detected using module's
        effects. Engine relies on assumption that each module has at max one
        such effect. This type of check is better to be performed after data
        cleanup, because slot type effects are still used on many item types we
        do not need and want to remove to avoid printing unnecessary log
        entries.

        Args:
            dte_rows: Iterable with data rows from dgmtypeeffects table.
        """
        rack_effects = (
            EffectId.hi_power, EffectId.med_power, EffectId.lo_power
        )
        racked_items = set()
        invalid_rows = set()
        for row in sorted(dte_rows, key=lambda r: r['table_pos']):
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
            msg = (
                '{} rows contain colliding module racks, removing them'
            ).format(len(invalid_rows))
            logger.warning(msg)
            dte_rows.difference_update(invalid_rows)
