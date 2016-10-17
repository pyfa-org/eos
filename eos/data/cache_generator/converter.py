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


import re
from logging import getLogger

from eos.const.eve import Attribute, Operand
from eos.util.frozen_dict import FrozenDict
from .modifier_builder import ModifierBuilder


logger = getLogger(__name__)


class Converter:
    """
    Class responsible for transforming data structure,
    like moving data around or converting whole data
    structure.
    """

    def normalize(self, data):
        """ Make data more consistent."""
        self.data = data
        self._move_attribs()
        self._convert_expression_symbolic_references()

    def _move_attribs(self):
        """
        Some of item attributes are defined in evetypes table.
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
        successes = 0
        failures = 0
        data = self.data
        dgmexpressions = data['dgmexpressions']
        replacement_desc = (
            ('dgmattribs', 'attributeID', 'attributeName', 'expressionAttributeID', Operand.def_attr),
            ('evegroups', 'groupID', 'groupName_en-us', 'expressionGroupID', Operand.def_grp),
            ('evetypes', 'typeID', 'typeName_en-us', 'expressionTypeID', Operand.def_type)
        )
        for entry in replacement_desc:
            entity_table, id_column, symname_column, tgt_column, operand = entry
            name_id_map = {}
            for entity_row in sorted(data[entity_table], key=lambda row: row['table_pos']):
                entity_id = entity_row[id_column]
                entity_name_normal = entity_row.get(symname_column)
                if not entity_name_normal:
                    continue
                ids_normal = name_id_map.setdefault(entity_name_normal, [])
                ids_normal.append(entity_id)
                # Entities can be referred via names with stripped space
                entity_name_stripped = re.sub('\s', '', entity_name_normal)
                # Do not add id of entity against stripped name, if it's
                # already stripped
                if entity_name_stripped == entity_name_normal:
                    continue
                ids_stripped = name_id_map.setdefault(entity_name_stripped, [])
                ids_stripped.append(entity_id)
            # Set to keep symbolic names about which we've already
            # logged warnings
            warned_conflicts = set()
            # We're modifying only rows with specific operands
            for exp_row in filter(lambda r: r['operandID'] == operand, dgmexpressions):
                exp_entity_id = exp_row[tgt_column]
                # If entity is already referenced via ID, nothing
                # to do here
                if exp_entity_id is not None:
                    continue
                sym_name = exp_row['expressionValue']
                # If we don't have expression value in our name-id map,
                # then we can't help anyhow too
                if sym_name not in name_id_map:
                    failures += 1
                    continue
                repl_ids = name_id_map[sym_name]
                repl_id = repl_ids[0]
                if len(repl_ids) > 1:
                    if sym_name not in warned_conflicts:
                        msg = 'multiple {}s found for symbolic name "{}": ({}), using {}'.format(
                            id_column, sym_name, ', '.join(str(i) for i in repl_ids), repl_id)
                        logger.warning(msg)
                        warned_conflicts.add(sym_name)
                # As rows are frozen dicts, we compose new mutable dict, update
                # data there, freeze it, and add to replacement maps
                new_exp_row = {}
                new_exp_row.update(exp_row)
                new_exp_row['expressionValue'] = None
                new_exp_row[tgt_column] = repl_id
                new_exp_row = FrozenDict(new_exp_row)
                dgmexpressions.remove(exp_row)
                dgmexpressions.add(new_exp_row)
                successes += 1
        # Report results to log, it will help to indicate when CCP finally stops
        # using literal references, and we can get rid of this conversion
        msg = 'conversion of literal references to IDs in dgmexpressions: {} successful, {} failed'.format(
            successes, failures)
        logger.info(msg)

    def convert(self, data):
        """
        Convert database-like data structure to eos-
        specific one.
        """
        data = self._assemble(data)
        self._build_modifiers(data)
        return data

    def _assemble(self, data):
        """
        Use passed data to compose object-like data rows,
        as in, to 'assemble' objects.
        """
        # Before actually generating rows, we need to collect
        # some data in convenient form
        # Format: {type ID: type row}
        dgmeffects_keyed = {}
        for row in data['dgmeffects']:
            dgmeffects_keyed[row['effectID']] = row
        # Format: {group ID: group row}
        evegroups_keyed = {}
        for row in data['evegroups']:
            evegroups_keyed[row['groupID']] = row
        # Format: {type ID: default effect ID}
        type_defeff_map = {}
        for row in data['dgmtypeeffects']:
            if row.get('isDefault') is True:
                type_defeff_map[row['typeID']] = row['effectID']
        # Format: {type ID: [effect IDs]}
        type_effects = {}
        for row in data['dgmtypeeffects']:
            type_effects_row = type_effects.setdefault(row['typeID'], [])
            type_effects_row.append(row['effectID'])
        # Format: {type ID: {attr ID: value}}
        type_attribs = {}
        for row in data['dgmtypeattribs']:
            type_attribs_row = type_attribs.setdefault(row['typeID'], {})
            type_attribs_row[row['attributeID']] = row['value']

        # We will build new data structure from scratch
        assembly = {}

        types = []
        for row in data['evetypes']:
            type_id = row['typeID']
            group = row.get('groupID')
            type_ = {
                'type_id': type_id,
                'group': group,
                'category': evegroups_keyed.get(group, {}).get('categoryID'),
                'effects': type_effects.get(type_id, []),
                'attributes': type_attribs.get(type_id, {}),
                'default_effect': type_defeff_map.get(type_id)
            }
            types.append(type_)
        assembly['types'] = types

        attributes = []
        for row in data['dgmattribs']:
            attribute = {
                'attribute_id': row['attributeID'],
                'max_attribute': row.get('maxAttributeID'),
                'default_value': row.get('defaultValue'),
                'high_is_good': row.get('highIsGood'),
                'stackable': row.get('stackable')
            }
            attributes.append(attribute)
        assembly['attributes'] = attributes

        effects = []
        assembly['effects'] = []
        for row in data['dgmeffects']:
            effect = {
                'effect_id': row['effectID'],
                'effect_category': row.get('effectCategory'),
                'is_offensive': row.get('isOffensive'),
                'is_assistance': row.get('isAssistance'),
                'duration_attribute': row.get('durationAttributeID'),
                'discharge_attribute': row.get('dischargeAttributeID'),
                'range_attribute': row.get('rangeAttributeID'),
                'falloff_attribute': row.get('falloffAttributeID'),
                'tracking_speed_attribute': row.get('trackingSpeedAttributeID'),
                'fitting_usage_chance_attribute': row.get('fittingUsageChanceAttributeID'),
                'pre_expression': row.get('preExpression'),
                'post_expression': row.get('postExpression'),
                'modifier_info': row.get('modifierInfo')
            }
            effects.append(effect)
        assembly['effects'] = effects

        assembly['expressions'] = list(data['dgmexpressions'])

        return assembly

    def _build_modifiers(self, data):
        """
        Replace expressions with generated out of
        them modifiers.
        """
        builder = ModifierBuilder(data['expressions'])
        # Lists effects, which are using given modifier
        # Format: {modifier row: [effect IDs]}
        modifier_effect_map = {}
        # Prepare to give each modifier unique ID
        # Format: {modifier row: modifier ID}
        modifier_id_map = {}
        modifier_id = 1
        # Sort rows by ID so we numerate modifiers in deterministic way
        for effect_row in sorted(data['effects'], key=lambda row: row['effect_id']):
            modifiers, build_status = builder.build(effect_row)
            # Update effects: add modifier build status and remove
            # fields which we needed only for this process
            effect_row['build_status'] = build_status
            del effect_row['pre_expression']
            del effect_row['post_expression']
            del effect_row['modifier_info']
            for modifier in modifiers:
                # Convert modifiers into frozen datarows to use
                # them in conversion process
                frozen_modifier = self._freeze_modifier(modifier)
                # Gather data about which effects use which modifier
                used_by_effects = modifier_effect_map.setdefault(frozen_modifier, [])
                used_by_effects.append(effect_row['effect_id'])
                # Assign ID only to each unique modifier
                if frozen_modifier not in modifier_id_map:
                    modifier_id_map[frozen_modifier] = modifier_id
                    modifier_id += 1

        # Compose reverse to modifier_effect_map dictionary
        # Format: {effect ID: [modifier rows]}
        effect_modifier_map = {}
        for frozen_modifier, effect_ids in modifier_effect_map.items():
            for effect_id in effect_ids:
                effect_modifiers = effect_modifier_map.setdefault(effect_id, [])
                effect_modifiers.append(frozen_modifier)

        # For each effect, add IDs of each modifiers it uses
        for effect_row in data['effects']:
            modifier_ids = []
            for frozen_modifier in effect_modifier_map.get(effect_row['effect_id'], ()):
                modifier_ids.append(modifier_id_map[frozen_modifier])
            effect_row['modifiers'] = modifier_ids

        # Replace expressions table with modifiers
        del data['expressions']
        modifiers = []
        for frozen_modifier, modifier_id in modifier_id_map.items():
            modifier = {}
            modifier.update(frozen_modifier)
            modifier['modifier_id'] = modifier_id
            modifiers.append(modifier)
        data['modifiers'] = modifiers

    def _freeze_modifier(self, modifier):
        """
        Converts modifier into frozendict with its keys and
        values assigned according to modifier's ones.
        """
        # Fields which we need to write into row
        fields = (
            'state',
            'scope',
            'src_attr',
            'operator',
            'tgt_attr',
            'domain',
            'filter_type',
            'filter_value'
        )
        modifier_row = {}
        for field in fields:
            modifier_row[field] = getattr(modifier, field)
        frozen_row = FrozenDict(modifier_row)
        return frozen_row
