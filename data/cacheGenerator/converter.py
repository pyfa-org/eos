#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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
#===============================================================================


from eos.eve.const import Attribute
from eos.util.frozendict import frozendict
from .modifierBuilder.modifierBuilder import ModifierBuilder


class Converter:
    """
    Class responsible for transforming data structure,
    like moving data around or converting whole data
    structure.
    """

    def __init__(self, logger):
        self._logger = logger

    def normalize(self, data):
        """ Make data more consistent."""
        self.data = data
        self._moveAttribs()

    def _moveAttribs(self):
        """
        Some of item attributes are defined in invtypes table.
        We do not need them there, for data consistency it's worth
        to move them to dgmtypeattribs table.
        """
        atrribMap = {'radius': Attribute.radius,
                     'mass': Attribute.mass,
                     'volume': Attribute.volume,
                     'capacity': Attribute.capacity}
        attrIds = tuple(atrribMap.values())
        # Here we will store pairs (typeID, attrID) already
        # defined in table
        definedPairs = set()
        dgmtypeattribs = self.data['dgmtypeattribs']
        for row in dgmtypeattribs:
            if row['attributeID'] not in attrIds:
                continue
            definedPairs.add((row['typeID'], row['attributeID']))
        attrsSkipped = 0
        newInvtypes = set()
        # Cycle through all invtypes, for each row moving each its field
        # either to different table or container for updated rows
        for row in self.data['invtypes']:
            typeId = row['typeID']
            newRow = {}
            for field, value in row.items():
                if field in atrribMap:
                    # If row didn't have such attribute defined, skip it
                    if value is None:
                        continue
                    # If such attribute already exists in dgmtypeattribs,
                    # do not modify it - values from dgmtypeattribs table
                    # have priority
                    attrId = atrribMap[field]
                    if (typeId, attrId) in definedPairs:
                        attrsSkipped += 1
                        continue
                    # Generate row and add it to proper attribute table
                    dgmtypeattribs.add(frozendict({'typeID': typeId, 'attributeID': attrId, 'value': value}))
                else:
                    newRow[field] = value
            newInvtypes.add(frozendict(newRow))
        # Update invtypes with rows which do not contain attributes
        self.data['invtypes'].clear()
        self.data['invtypes'].update(newInvtypes)
        if attrsSkipped > 0:
            msg = '{} built-in attributes already have had value in dgmtypeattribs and were skipped'.format(attrsSkipped)
            self._logger.warning(msg, childName='cacheGenerator')

    def convert(self, data):
        """
        Convert database-like data structure to eos-
        specific one.
        """
        data = self._assemble(data)
        self._buildModifiers(data)
        return data

    def _assemble(self, data):
        """
        Use passed data to compose object-like data rows,
        as in, to 'assemble' objects.
        """
        # Before actually generating rows, we need to collect
        # some data in convenient form
        # Format: {type ID: type row}
        dgmeffectsKeyed = {}
        for row in data['dgmeffects']:
            dgmeffectsKeyed[row['effectID']] = row
        # Format: {group ID: group row}
        invgroupsKeyed = {}
        for row in data['invgroups']:
            invgroupsKeyed[row['groupID']] = row
        # Format: {type ID: default effect ID}
        typeDefeffMap = {}
        for row in data['dgmtypeeffects']:
            if row.get('isDefault') is True:
                typeDefeffMap[row['typeID']] = row['effectID']
        # Format: {type ID: [effect IDs]}
        typeEffects = {}
        for row in data['dgmtypeeffects']:
            typeEffectsRow = typeEffects.setdefault(row['typeID'], [])
            typeEffectsRow.append(row['effectID'])
        # Format: {type ID: {attr ID: value}}
        typeAttribs = {}
        for row in data['dgmtypeattribs']:
            typeAttribsRow = typeAttribs.setdefault(row['typeID'], {})
            typeAttribsRow[row['attributeID']] = row['value']

        # We will build new data structure from scratch
        assembly = {}

        types = []
        for row in data['invtypes']:
            typeId = row['typeID']
            groupId = row.get('groupID')
            # Get effect row of default effect, replacing it
            # with empty dictionary if there's no one
            if typeId in typeDefeffMap:
                defeff = dgmeffectsKeyed.get(typeDefeffMap[typeId], {})
            else:
                defeff = {}
            type_ = {'typeId': typeId,
                     'groupId': groupId,
                     'categoryId': invgroupsKeyed.get(groupId, {}).get('categoryID'),
                     'durationAttributeId': defeff.get('durationAttributeID'),
                     'dischargeAttributeId': defeff.get('dischargeAttributeID'),
                     'rangeAttributeId': defeff.get('rangeAttributeID'),
                     'falloffAttributeId': defeff.get('falloffAttributeID'),
                     'trackingSpeedAttributeId': defeff.get('trackingSpeedAttributeID'),
                     'fittableNonSingleton': invgroupsKeyed.get(groupId, {}).get('fittableNonSingleton'),
                     'effects': typeEffects.get(typeId, []),
                     'attributes': typeAttribs.get(typeId, {})}
            types.append(type_)
        assembly['types'] = types

        attributes = []
        for row in data['dgmattribs']:
            attribute = {'attributeId': row['attributeID'],
                         'maxAttributeId': row.get('maxAttributeID'),
                         'defaultValue': row.get('defaultValue'),
                         'highIsGood': row.get('highIsGood'),
                         'stackable': row.get('stackable')}
            attributes.append(attribute)
        assembly['attributes'] = attributes

        effects = []
        assembly['effects'] = []
        for row in data['dgmeffects']:
            effect = {'effectId': row['effectID'],
                      'effectCategory': row.get('effectCategory'),
                      'isOffensive': row.get('isOffensive'),
                      'isAssistance': row.get('isAssistance'),
                      'fittingUsageChanceAttributeId': row.get('fittingUsageChanceAttributeID'),
                      'preExpressionId': row.get('preExpression'),
                      'postExpressionId': row.get('postExpression')}
            effects.append(effect)
        assembly['effects'] = effects

        assembly['expressions'] = list(data['dgmexpressions'])

        return assembly

    def _buildModifiers(self, data):
        """
        Replace expressions with generated out of
        them modifiers.
        """
        builder = ModifierBuilder(data['expressions'], self._logger)
        # Lists effects, which are using given modifier
        # Format: {modifier row: [effect IDs]}
        modifierEffectMap = {}
        # Prepare to give each modifier unique ID
        # Format: {modifier row: modifier ID}
        modifierIdMap = {}
        modifierId = 1
        # Sort rows by ID so we numerate modifiers in deterministic way
        for effectRow in sorted(data['effects'], key=lambda row: row['effectId']):
            modifiers, buildStatus = builder.buildEffect(effectRow['preExpressionId'],
                                                         effectRow['postExpressionId'],
                                                         effectRow['effectCategory'])
            # Update effects: add modifier build status and remove
            # fields which we needed only for this process
            effectRow['buildStatus'] = buildStatus
            del effectRow['preExpressionId']
            del effectRow['postExpressionId']
            for modifier in modifiers:
                # Convert modifiers into frozen datarows to use
                # them in conversion process
                frozenModifier = self._freezeModifier(modifier)
                # Gather data about which effects use which modifier
                usedByEffects = modifierEffectMap.setdefault(frozenModifier, [])
                usedByEffects.append(effectRow['effectId'])
                # Assign ID only to each unique modifier
                if frozenModifier not in modifierIdMap:
                    modifierIdMap[frozenModifier] = modifierId
                    modifierId += 1

        # Compose reverse to modifierEffectMap dictionary
        # Format: {effect ID: [modifier rows]}
        effectModifierMap = {}
        for frozenModifier, effectIds in modifierEffectMap.items():
            for effectId in effectIds:
                effectModifiers = effectModifierMap.setdefault(effectId, [])
                effectModifiers.append(frozenModifier)

        # For each effect, add IDs of each modifiers it uses
        for effectRow in data['effects']:
            modifiers = []
            for frozenModifier in effectModifierMap.get(effectRow['effectId'], ()):
                modifiers.append(modifierIdMap[frozenModifier])
            effectRow['modifiers'] = modifiers

        # Replace expressions table with modifiers
        del data['expressions']
        modifiers = []
        for frozenModifier, modifierId in modifierIdMap.items():
            modifier = {}
            modifier.update(frozenModifier)
            modifier['modifierId'] = modifierId
            modifiers.append(modifier)
        data['modifiers'] = modifiers

    def _freezeModifier(self, modifier):
        """
        Converts modifier into frozendict with its keys and
        values assigned according to modifier's ones.
        """
        # Fields which we need to dump into row
        fields = ('state', 'context', 'sourceAttributeId', 'operator',
                  'targetAttributeId', 'location', 'filterType', 'filterValue')
        modifierRow = {}
        for field in fields:
            modifierRow[field] = getattr(modifier, field)
        frozenRow = frozendict(modifierRow)
        return frozenRow
