#!/usr/bin/env python3
#===============================================================================
# Copyright (C) 2012 Anton Vorobyov
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


"""
Takes JSON produced by Phobos and adapts it into form acceptable for Eos,
You can find Phobos at http://fisheye.evefit.org/browse/phobos
"""


if __name__ == '__main__':


    import argparse
    import bz2
    import json
    import os.path


    parser = argparse.ArgumentParser(description='This script converts Phobos-produced JSON and converts into Eos-specific form.')
    parser.add_argument('source', type=str, help='path to the folder with source JSON data')
    parser.add_argument('-d', '--dest', type=str, dest='dest', default='', help='path to output folder')
    args = parser.parse_args()

    base = os.path.expanduser(args.source)
    dest = os.path.expanduser(args.dest)

    print('Loading data...')
    with open(os.path.join(base, 'invtypes.json'), mode='r') as file:
        invtypes_raw = json.load(file)
    with open(os.path.join(base, 'invgroups.json'), mode='r') as file:
        invgroups_raw = json.load(file)
    with open(os.path.join(base, 'dgmattribs.json'), mode='r') as file:
        dgmattribs_raw = json.load(file)
    with open(os.path.join(base, 'dgmtypeattribs.json'), mode='r') as file:
        dgmtypeattribs_raw = json.load(file)
    with open(os.path.join(base, 'dgmeffects.json'), mode='r') as file:
        dgmeffects_raw = json.load(file)
    with open(os.path.join(base, 'dgmtypeeffects.json'), mode='r') as file:
        dgmtypeeffects_raw = json.load(file)
    with open(os.path.join(base, 'dgmexpressions.json'), mode='r') as file:
        dgmexpressions_raw = json.load(file)

    # Effects ID-keyed dictionary iss used in multiple places,
    # so we create it here
    dgmeffects = {}
    for row in dgmeffects_raw:
        effectID = row['effectID']
        if effectID in dgmeffects:
            print("  Warning: duplicate effectID {}".format(effectID))
            continue
        dgmeffects[effectID] = row

    print("Dumping types...")
    types = {}
    # Before actually filling dictionary, collect additional data
    # to avoid looking up lists for each item
    # Format: {groupID: group row}
    invgroups = {}
    for row in invgroups_raw:
        groupID = row['groupID']
        if groupID in invgroups:
            print("  Warning: duplicate groupID {}".format(groupID))
            continue
        invgroups[groupID] = row
    # Format: {typeID: default effect}
    type_defeff = {}
    for row in dgmtypeeffects_raw:
        # Skip non-default effects
        if not row.get('isDefault'):
            continue
        typeID = row['typeID']
        if typeID in type_defeff:
            print("  Warning: multiple default effects for type {}".format(typeID))
            continue
        type_defeff[typeID] = row.get('effectID')
    # Format: {typeID: [effectIDs]}
    type_effects = {}
    for row in dgmtypeeffects_raw:
        typeID = row['typeID']
        effectID = row['effectID']
        data = type_effects.setdefault(typeID, [])
        if effectID in data:
            print("  Warning: duplicate effects on type {}".format(typeID))
        data.append(effectID)
    # Format: {typeID: {attrID: value}}
    type_attribs = {}
    for row in dgmtypeattribs_raw:
        typeID = row['typeID']
        data = type_attribs.setdefault(typeID, {})
        attrID = row['attributeID']
        if attrID in data:
            print("  Warning: multiple values of the same attribute on type {}".format(typeID))
            continue
        data[attrID] = row.get('value')
    for row in invtypes_raw:
        typeID = row['typeID']
        if typeID in types:
            print("  Warning: duplicate typeID {}".format(typeID))
            continue
        groupID = row.get('groupID')
        # Get effect row of default effect, replacing it
        # with empty dictionary if there's no one
        if typeID in type_defeff:
            defeff = dgmeffects.get(type_defeff[typeID], {})
        else:
            defeff = {}
        types[typeID] = (groupID,
                         invgroups.get(groupID, {}).get('categoryID'),
                         defeff.get('durationAttributeID'),
                         defeff.get('dischargeAttributeID'),
                         defeff.get('rangeAttributeID'),
                         defeff.get('falloffAttributeID'),
                         defeff.get('trackingSpeedAttributeID'),
                         invgroups.get(groupID, {}).get('fittableNonSingleton'),
                         tuple(type_effects.get(typeID, ())),
                         tuple(type_attribs.get(typeID, {}).items()))
    with bz2.BZ2File(os.path.join(dest, 'types.json.bz2'), 'wb') as file:
        file.write(json.dumps(types).encode('utf-8'))

    print("Dumping attributes...")
    attributes = {}
    for row in dgmattribs_raw:
        attrID = row['attributeID']
        if attrID in attributes:
            print("  Warning: duplicate attributeID {}".format(attrID))
            continue
        attributes[attrID] = (row.get('maxAttributeID'),
                              row.get('defaultValue'),
                              row.get('highIsGood'),
                              row.get('stackable'))
    with bz2.BZ2File(os.path.join(dest, 'attributes.json.bz2'), 'wb') as file:
        file.write(json.dumps(attributes).encode('utf-8'))

    print("Dumping effects...")
    effects = {}
    for effectID, data in dgmeffects.items():
        effects[effectID] = (data.get('effectCategory'),
                             data.get('isOffensive'),
                             data.get('isAssistance'),
                             data.get('fittingUsageChanceAttributeID'),
                             data.get('preExpression'),
                             data.get('postExpression'))
    with bz2.BZ2File(os.path.join(dest, 'effects.json.bz2'), 'wb') as file:
        file.write(json.dumps(effects).encode('utf-8'))

    print("Dumping expressions...")
    expressions = {}
    for row in dgmexpressions_raw:
        expID = row['expressionID']
        if expID in expressions:
            print("  Warning: duplicate expressionID {}".format(expID))
            continue
        expressions[expID] = (row.get('operandID'),
                              row.get('arg1'),
                              row.get('arg2'),
                              row.get('expressionValue'),
                              row.get('expressionTypeID'),
                              row.get('expressionGroupID'),
                              row.get('expressionAttributeID'))
    with bz2.BZ2File(os.path.join(dest, 'expressions.json.bz2'), 'wb') as file:
        file.write(json.dumps(expressions).encode('utf-8'))

    print("Done")
