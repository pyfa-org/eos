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

from eos.const.eve import Attribute, Group, Operand
from eos.util.frozen_dict import FrozenDict
from .modifier_builder import ModifierBuilder


logger = getLogger(__name__)


class Normalizer:

    def normalize(self, data):
        """ Make data format more consistent."""
        self.data = data
        self._move_attribs()
        self._convert_expression_symbolic_references()

    def _move_attribs(self):
        """
        Some of eve type attributes are defined in evetypes table.
        We do not need them there, for data consistency it's worth
        to move them to dgmtypeattribs table.
        """
        atrrib_map = {
            'radius': Attribute.radius,
            'mass': Attribute.mass,
            'volume': Attribute.volume,
            'capacity': Attribute.capacity
        }
        attr_ids = tuple(atrrib_map.values())
        # Here we will store pairs (typeID, attrID) already
        # defined in table
        defined_pairs = set()
        dgmtypeattribs = self.data['dgmtypeattribs']
        for row in dgmtypeattribs:
            if row['attributeID'] not in attr_ids:
                continue
            defined_pairs.add((row['typeID'], row['attributeID']))
        attrs_skipped = 0
        new_evetypes = set()
        # Cycle through all evetypes, for each row moving each its field
        # either to different table or container for updated rows
        for row in self.data['evetypes']:
            type_id = row['typeID']
            new_row = {}
            for field, value in row.items():
                if field in atrrib_map:
                    # If row didn't have such attribute defined, skip it
                    if value is None:
                        continue
                    # If such attribute already exists in dgmtypeattribs,
                    # do not modify it - values from dgmtypeattribs table
                    # have priority
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
        self.data['evetypes'].clear()
        self.data['evetypes'].update(new_evetypes)
        if attrs_skipped > 0:
            msg = '{} built-in attributes already have had value in dgmtypeattribs and were skipped'.format(
                attrs_skipped)
            logger.warning(msg)

    def _convert_expression_symbolic_references(self):
        """
        Some of entities in dgmexpressions table are defined not as
        IDs, but as symbolic references. Convert them to IDs here.
        """
        data = self.data
        dgmexpressions = data['dgmexpressions']
        # Format: ((operator, column name for entity ID, {replacement_map}, (ignored names, ...)), ...)
        replacement_spec = (
            (Operand.def_attr, 'expressionAttributeID', {}, ('shieldDamage',)),
            (
                Operand.def_grp, 'expressionGroupID',
                {
                    'EnergyWeapon': Group.energy_weapon,
                    'HybridWeapon': Group.hydrid_weapon,
                    'MiningLaser': Group.mining_laser,
                    'ProjectileWeapon': Group.projectile_weapon
                },
                ('Structure', 'PowerCore', '    None')
            ),
            (Operand.def_type, 'expressionTypeID', {}, ('Acceration Control',))
        )
        for operand, id_column_name, replacements, ignored_names in replacement_spec:
            used_replacements = set()
            unknown_names = set()
            # We're modifying only rows with specific operands
            for expression_row in tuple(filter(lambda r: r['operandID'] == operand, dgmexpressions)):
                expression_entity_id = expression_row[id_column_name]
                # If entity is already referenced via ID, nothing
                # to do here
                if expression_entity_id is not None:
                    continue
                symbolic_entity_name = expression_row['expressionValue']
                # Skip names we've set to ignore explicitly
                if symbolic_entity_name in ignored_names:
                    continue
                # Do replacements if they're known to us
                if symbolic_entity_name in replacements:
                    # As rows are frozen dicts, we compose new mutable dict, update
                    # data there, freeze it, and do actual replacement
                    new_expression_row = {}
                    new_expression_row.update(expression_row)
                    new_expression_row['expressionValue'] = None
                    new_expression_row[id_column_name] = replacements[symbolic_entity_name]
                    new_expression_row = FrozenDict(new_expression_row)
                    dgmexpressions.remove(expression_row)
                    dgmexpressions.add(new_expression_row)
                    used_replacements.add(symbolic_entity_name)
                    continue
                # If we do not know it, add to special container which
                # We will use later
                unknown_names.add(symbolic_entity_name)
            # Report results to log, it will help to indicate when CCP finally stops
            # using literal references, and we can get rid of this conversion, or add
            # some new
            unused_replacements = set(replacements).difference(used_replacements)
            if len(unused_replacements) > 0:
                msg = '{} replacements for {} were not used: {}'.format(
                    len(unused_replacements), id_column_name,
                    ', '.join('"{}"'.format(name) for name in sorted(unused_replacements))
                )
                logger.warning(msg)
            if len(unknown_names) > 0:
                msg = 'unable to convert {} literal references to {}: {}'.format(
                    len(unknown_names), id_column_name,
                    ', '.join('"{}"'.format(name) for name in sorted(unknown_names))
                )
                logger.warning(msg)
