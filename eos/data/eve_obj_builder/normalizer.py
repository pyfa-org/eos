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

from eos.const.eve import AttributeId, GroupId, OperandId
from eos.util.frozen_dict import FrozenDict


logger = getLogger(__name__)


class Normalizer:

    @staticmethod
    def run(data):
        """Normalize passed data.

        Data provided by data handler has been (deliberately) denormalized by
        CCP due to unknown reasons. As we do not care about reasons, normalize
        data for easier and hack-free code in other parts of Eos.

        Args:
            data: Dictionary in {table name: {table, rows}} format.
        """
        Normalizer._move_attribs(data)
        Normalizer._convert_expression_symbolic_references(data)

    @staticmethod
    def _move_attribs(data):
        """Normalize attribute value definitions.

        Some of eve type attributes are defined in evetypes table. We do not
        need them there, for data consistency it's worth to move them to
        dgmtypeattribs table, where the rest of attributes are defined.

        Args:
            data: Dictionary in {table name: {table, rows}} format.
        """
        atrrib_map = {
            'radius': AttributeId.radius,
            'mass': AttributeId.mass,
            'volume': AttributeId.volume,
            'capacity': AttributeId.capacity
        }
        attr_ids = tuple(atrrib_map.values())
        # Here we will store pairs (typeID, attrID) already defined in
        # dgmtypeattribs
        defined_pairs = set()
        dgmtypeattribs = data['dgmtypeattribs']
        for row in dgmtypeattribs:
            if row['attributeID'] not in attr_ids:
                continue
            defined_pairs.add((row['typeID'], row['attributeID']))
        attrs_skipped = 0
        new_evetypes = set()
        # Cycle through all evetypes, for each row moving each its field either
        # to different table or container for updated rows
        for row in data['evetypes']:
            type_id = row['typeID']
            new_row = {}
            for field, value in row.items():
                if field in atrrib_map:
                    # If row didn't have such attribute defined, skip it
                    if value is None:
                        continue
                    # If such attribute already exists in dgmtypeattribs, do not
                    # modify it - values from dgmtypeattribs table have priority
                    attr_id = atrrib_map[field]
                    if (type_id, attr_id) in defined_pairs:
                        attrs_skipped += 1
                        continue
                    # Generate row and add it to proper attribute table
                    dgmtypeattribs.add(FrozenDict({
                        'typeID': type_id,
                        'attributeID': attr_id,
                        'value': value
                    }))
                else:
                    new_row[field] = value
            new_evetypes.add(FrozenDict(new_row))
        # Update evetypes with rows which do not contain attributes
        data['evetypes'].clear()
        data['evetypes'].update(new_evetypes)
        if attrs_skipped > 0:
            msg = (
                '{} built-in attributes already have had value in '
                'dgmtypeattribs and were skipped'
            ).format(attrs_skipped)
            logger.warning(msg)

    @staticmethod
    def _convert_expression_symbolic_references(data):
        """Convert all known symbolic references to int references.

        Some of entities in dgmexpressions table are defined not as IDs, but as
        symbolic references. CCP most likely has these symbolic names defined in
        their code, thus we have to hardcode it too.

        Args:
            data: Dictionary in {table name: {table, rows}} format.
        """
        dgmexps = data['dgmexpressions']
        # Replacement specification
        # Format:
        # (
        #   (
        #     operator,
        #     column name for entity ID,
        #     {replacement: map},
        #     (ignored names, ...)
        #   ),
        #   ...
        # )
        repl_spec = (
            (
                OperandId.def_attr,
                'expressionAttributeID',
                {},
                ('shieldDamage',)
            ),
            (
                OperandId.def_grp,
                'expressionGroupID',
                {
                    'EnergyWeapon': GroupId.energy_weapon,
                    'HybridWeapon': GroupId.hydrid_weapon,
                    'MiningLaser': GroupId.mining_laser,
                    'ProjectileWeapon': GroupId.projectile_weapon
                },
                ('Structure', 'PowerCore', '    None')
            ),
            (
                OperandId.def_type,
                'expressionTypeID',
                {},
                ('Acceration Control',)
            )
        )
        for operand, id_col_name, repls, ignored_names in repl_spec:
            used_repls = set()
            unknown_names = set()
            # We're modifying only rows with specific operands
            for exp_row in dgmexps:
                if exp_row['operandID'] != operand:
                    continue
                exp_entity_id = exp_row[id_col_name]
                # If entity is already referenced via ID, nothing to do here
                if exp_entity_id is not None:
                    continue
                symbolic_entity_name = exp_row['expressionValue']
                # Skip names we've set to ignore explicitly
                if symbolic_entity_name in ignored_names:
                    continue
                # Do replacements if they're known to us
                if symbolic_entity_name in repls:
                    # As rows are frozen dicts, we compose new mutable dict,
                    # update data there, freeze it, and do actual replacement
                    new_exp_row = {}
                    new_exp_row.update(exp_row)
                    new_exp_row['expressionValue'] = None
                    new_exp_row[id_col_name] = repls[symbolic_entity_name]
                    new_exp_row = FrozenDict(new_exp_row)
                    dgmexps.remove(exp_row)
                    dgmexps.add(new_exp_row)
                    used_repls.add(symbolic_entity_name)
                    continue
                # If we do not know it, add to special container which we will
                # use later
                unknown_names.add(symbolic_entity_name)
            # Report results to log, it will help to indicate when CCP finally
            # stops using literal references, and we can get rid of this
            # conversion, or add some new
            unused_repls = set(repls).difference(used_repls)
            if unused_repls:
                unused_repls = sorted(unused_repls)
                unused_line = ', '.join('"{}"'.format(r) for r in unused_repls)
                msg = '{} replacements for {} were not used: {}'.format(
                    len(unused_repls), id_col_name, unused_line)
                logger.warning(msg)
            if unknown_names:
                unknown_names = sorted(unknown_names)
                unknown_line = ', '.join(
                    '"{}"'.format(n) for n in unknown_names)
                msg = (
                    'unable to convert {} literal references to {}: {}'
                ).format(len(unknown_names), id_col_name, unknown_line)
                logger.warning(msg)
