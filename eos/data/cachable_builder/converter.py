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

from eos.data.cachable import Attribute, Effect, Type
from .modifier_builder import ModifierBuilder


logger = getLogger(__name__)


class Converter:

    @staticmethod
    def run(data):
        """
        Convert data into Eos cachable objects.
        """
        # Before actually instantiating anything, we need to collect
        # some data in convenient form
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
            type_effects.setdefault(row['typeID'], []).append(row['effectID'])
        # Format: {type ID: {attr ID: value}}
        type_attribs = {}
        for row in data['dgmtypeattribs']:
            type_attribs.setdefault(row['typeID'], {})[row['attributeID']] = row['value']
        # Format: {type ID: {ability ID: ability data}}
        typeabils_reformat = {}
        for row in data['typefighterabils']:
            type_abils = typeabils_reformat.setdefault(row['typeID'], {})
            type_abils[row['abilityID']] = {
                'cooldown_time': row.get('cooldownSeconds'),
                'charge_amount': row.get('chargeCount'),
                'charge_rearm_time': row.get('rearmTimeSeconds')
            }

        # Convert attributes
        attributes = {}
        for row in data['dgmattribs']:
            attribute = Attribute(
                attribute_id=row['attributeID'],
                max_attribute=row.get('maxAttributeID'),
                default_value=row.get('defaultValue'),
                high_is_good=row.get('highIsGood'),
                stackable=row.get('stackable')
            )
            attributes[attribute.id] = attribute

        # Convert effects
        effects = {}
        mod_builder = ModifierBuilder(data['dgmexpressions'])
        for row in data['dgmeffects']:
            modifiers, build_status = mod_builder.build(row)
            effect = Effect(
                effect_id=row['effectID'],
                category=row.get('effectCategory'),
                is_offensive=row.get('isOffensive'),
                is_assistance=row.get('isAssistance'),
                duration_attribute=row.get('durationAttributeID'),
                discharge_attribute=row.get('dischargeAttributeID'),
                range_attribute=row.get('rangeAttributeID'),
                falloff_attribute=row.get('falloffAttributeID'),
                tracking_speed_attribute=row.get('trackingSpeedAttributeID'),
                fitting_usage_chance_attribute=row.get('fittingUsageChanceAttributeID'),
                build_status=build_status,
                modifiers=tuple(modifiers),
                customize=False
            )
            effects[effect.id] = effect

        # Convert types
        types = {}
        for row in data['evetypes']:
            type_id = row['typeID']
            group = row.get('groupID')
            eve_type = Type(
                type_id=type_id,
                group=group,
                category=evegroups_keyed.get(group, {}).get('categoryID'),
                attributes=type_attribs.get(type_id, {}),
                effects=tuple(effects[eid] for eid in type_effects.get(type_id, ()) if eid in effects),
                default_effect=effects.get(type_defeff_map.get(type_id)),
                fighter_abilities=typeabils_reformat.get(type_id, {}),
                customize=False
            )
            types[eve_type.id] = eve_type

        return types, attributes, effects
