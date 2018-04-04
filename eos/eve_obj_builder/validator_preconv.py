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
from numbers import Real

from eos.const.eve import EffectId
from eos.const.eve import fighter_ability_map
from eos.util.frozendict import frozendict


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
        ValidatorPreConv._attr_value_type(data['dgmtypeattribs'])
        ValidatorPreConv._multiple_default_effects(data['dgmtypeeffects'])
        ValidatorPreConv._colliding_module_racks(data['dgmtypeeffects'])
        ValidatorPreConv._fighter_unknown_ability(data['typefighterabils'])
        ValidatorPreConv._fighter_ability_collisions(data['typefighterabils'])
        ValidatorPreConv._fighter_ability_effect(
            data['typefighterabils'], data['dgmtypeeffects'])

    @staticmethod
    def _attr_value_type(dta_rows):
        """Make sure that all attributes have numeric values."""
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
        """Check that each type has one default effect maximum."""
        # Set with IDs of item types, which have default effect
        defeff_type_ids = set()
        invalid_rows = set()
        for row in sorted(dte_rows, key=lambda r: r['table_pos']):
            is_default = row.get('isDefault')
            # We're interested only in default effects
            if not is_default:
                continue
            type_id = row['typeID']
            # If we already saw default effect for given type ID, invalidate
            # current row
            if type_id in defeff_type_ids:
                invalid_rows.add(row)
            else:
                defeff_type_ids.add(type_id)
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
                dte_rows.add(frozendict(new_row))

    @staticmethod
    def _colliding_module_racks(dte_rows):
        """Check that items can be assigned into one module rack maximum.

        Type of slot into which module is placed is detected using module's
        effects. Engine relies on assumption that each module has at max one
        such effect. This type of check is better to be performed after data
        cleanup, because slot type effects are still used on many item types we
        do not need and want to remove to avoid printing unnecessary log
        entries.
        """
        rack_effect_ids = (
            EffectId.hi_power,
            EffectId.med_power,
            EffectId.lo_power)
        racked_type_ids = set()
        invalid_rows = set()
        for row in sorted(dte_rows, key=lambda r: r['table_pos']):
            effect_id = row['effectID']
            # We're not interested in anything besides rack effects
            if effect_id not in rack_effect_ids:
                continue
            type_id = row['typeID']
            if type_id in racked_type_ids:
                invalid_rows.add(row)
            else:
                racked_type_ids.add(type_id)
        if invalid_rows:
            msg = (
                '{} rows contain colliding module racks, removing them'
            ).format(len(invalid_rows))
            logger.warning(msg)
            dte_rows.difference_update(invalid_rows)

    @staticmethod
    def _fighter_unknown_ability(tfa_rows):
        """Check that eos knows all abilities.

        Without such knowledge, it's impossible to control effects bound to
        abilities.
        """
        invalid_rows = set()
        for row in tfa_rows:
            if row['abilityID'] not in fighter_ability_map:
                invalid_rows.add(row)
        if invalid_rows:
            msg = (
                '{} rows contain unknown fighter abilities, removing them'
            ).format(len(invalid_rows))
            logger.warning(msg)
            tfa_rows.difference_update(invalid_rows)

    @staticmethod
    def _fighter_ability_collisions(tfa_rows):
        """Check that there're no effect collisions for abilities.

        Any effect on any item must be controlled by 1 ability max. Otherwise,
        it might be unclear which ability-specific attributes (like cooldown)
        effect should use and what should happen when both abilities are active
        at the same time.
        """
        # Format: {(type ID, effect ID), ...}
        defined_pairs = set()
        invalid_rows = set()
        for row in sorted(tfa_rows, key=lambda r: r['table_pos']):
            ability_id = row['abilityID']
            effect_id = fighter_ability_map[ability_id]
            type_id = row['typeID']
            pair = (type_id, effect_id)
            if pair in defined_pairs:
                invalid_rows.add(row)
            else:
                defined_pairs.add(pair)
        if invalid_rows:
            msg = (
                '{} rows contain colliding fighter abilities, removing them'
            ).format(len(invalid_rows))
            logger.warning(msg)
            tfa_rows.difference_update(invalid_rows)

    @staticmethod
    def _fighter_ability_effect(tfa_rows, dte_rows):
        """Check that fighters with abilities have corresponding effects."""
        # Format: {type ID: {effect ID}}
        types_effect_ids = {}
        for row in dte_rows:
            type_effect_ids = types_effect_ids.setdefault(row['typeID'], set())
            type_effect_ids.add(row['effectID'])
        invalid_rows = set()
        for row in tfa_rows:
            ability_id = row['abilityID']
            effect_id = fighter_ability_map[ability_id]
            type_id = row['typeID']
            if effect_id not in types_effect_ids.get(type_id, ()):
                invalid_rows.add(row)
        if invalid_rows:
            msg = (
                '{} rows contain abilities without effect, removing them'
            ).format(len(invalid_rows))
            logger.warning(msg)
            tfa_rows.difference_update(invalid_rows)
