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


class Converter:
    """
    Class responsible for transforming data
    into eve objects of several types.

    Positional arguments:
    logger -- logger to use
    """

    def convert(self, data):
        """
        Convert database-like data structure to eos-
        specific objects.

        data -- data to convert

        Return value:
        Dictionary in following format:
        {object type: {object ID: object}}
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
