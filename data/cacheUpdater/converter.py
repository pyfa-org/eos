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


class Converter:
    """
    Class responsible for transforming data structure,
    like moving data around or converting whole data
    structure.

    Positional arguments:
    logger -- logger to use
    """

    def __init__(self, logger):
        self._logger = logger


    def normalize(self, data):
        """
        Make data more consistent.

        Positional arguments:
        data -- data to refactor
        """
        self.data = data
        self._moveAttribs()

    def convert(self, data):
        """
        Convert database-like data structure to eos-
        specific one.

        data -- data to refactor

        Return value:
        Dictionary in usual for this module data format,
        with refactored data
        """
        # We will build new data structure from scratch
        newData = {}
        newData['types'] = {}
        newData['attributes'] = {}
        newData['effects'] = {}
        newData['expressions'] = {}

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

        types = newData['types']
        for row in data['invtypes']:
            typeId = row['typeID']
            groupId = row.get('groupID')
            # Get effect row of default effect, replacing it
            # with empty dictionary if there's no one
            if typeId in typeDefeffMap:
                defeff = dgmeffectsKeyed.get(typeDefeffMap[typeId], {})
            else:
                defeff = {}
            types[typeId] = (groupId,
                             invgroupsKeyed.get(groupId, {}).get('categoryID'),
                             defeff.get('durationAttributeID'),
                             defeff.get('dischargeAttributeID'),
                             defeff.get('rangeAttributeID'),
                             defeff.get('falloffAttributeID'),
                             defeff.get('trackingSpeedAttributeID'),
                             invgroupsKeyed.get(groupId, {}).get('fittableNonSingleton'),
                             tuple(typeEffects.get(typeId, ())),
                             tuple(typeAttribs.get(typeId, {}).items()))

        attributes = newData['attributes']
        for row in data['dgmattribs']:
            attrId = row['attributeID']
            attributes[attrId] = (row.get('maxAttributeID'),
                                  row.get('defaultValue'),
                                  row.get('highIsGood'),
                                  row.get('stackable'))

        # Effects
        effects = newData['effects']
        for row in data['dgmeffects']:
            effectId = row['effectID']
            effects[effectId] = (row.get('effectCategory'),
                                 row.get('isOffensive'),
                                 row.get('isAssistance'),
                                 row.get('fittingUsageChanceAttributeID'),
                                 row.get('preExpression'),
                                 row.get('postExpression'))

        expressions = newData['expressions']
        for row in data['dgmexpressions']:
            expId = row['expressionID']
            expressions[expId] = (row.get('operandID'),
                                  row.get('arg1'),
                                  row.get('arg2'),
                                  row.get('expressionValue'),
                                  row.get('expressionTypeID'),
                                  row.get('expressionGroupID'),
                                  row.get('expressionAttributeID'))

        return newData

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
            self._logger.warning(msg, childName='cacheUpdater')
