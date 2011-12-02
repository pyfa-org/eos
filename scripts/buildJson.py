#!/usr/bin/env python3
#===============================================================================
# Copyright (C) 2011 Diego Duclos
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
buildJson.py script.
This script takes a sqlite cache dump as input and outputs two bz2 compressed json files. One for eve staticdata (invtypes, invtypeattribs, invtypeeffects) and another for expression data.
"""

import time
start = time.clock()

import argparse
import sqlite3
import json
import bz2

parser = argparse.ArgumentParser(description="This script takes a sqlite cache dump as input and outputs two bz2 compressed json files. One for eve staticdata (invtypes, invtypeattribs, invtypeeffects) and another for expression data.")
parser.add_argument("dbPath", type=str, help="The path to the sqlite cache dump")
parser.add_argument("-e", "--typedump", type=str, dest="typeDumpPath", default="types.json.bz2")
parser.add_argument("-x", "--expressiondump", type=str, dest="expressionDumpPath", default="expressions.json.bz2")
parser.add_argument("-f", "--effectDump", type=str, dest="effectDumpPath", default="effects.json.bz2")
args = parser.parse_args()

conn = sqlite3.connect(args.dbPath, detect_types=sqlite3.PARSE_COLNAMES | sqlite3.PARSE_DECLTYPES)
conn.row_factory = sqlite3.Row


# read in types
types = {}

print("dumping types")
for typeRow in conn.execute('SELECT typeID, groupID FROM invtypes'):
    effects = [effectRow["effectID"] for effectRow in conn.execute('SELECT effectID FROM dgmtypeeffects WHERE typeID = ?', (typeRow["typeID"],))]
    attributes = [(attributeRow["attributeID"], attributeRow["value"])
                    for attributeRow in conn.execute('SELECT attributeID, value FROM dgmtypeattribs WHERE typeID = ?', (typeRow["typeID"],))]

    types[typeRow["typeID"]] = {'effects': effects,
                                'attributes': attributes,
                                'group': typeRow["groupID"]};

# Dump them
with bz2.BZ2File(args.typeDumpPath, 'wb') as f:
    f.write(json.dumps(types).encode('utf-8'))

print("dumping expressions")
# read in expressions
expressions = {}
for row in conn.execute('SELECT * FROM dgmexpressions'):
    expressions[row["expressionID"]] = {'operand': row["operandID"],
                                        'value': row["expressionValue"],
                                        'typeID': row["expressionTypeID"],
                                        'groupID': row["expressionGroupID"],
                                        'attributeID': row["expressionAttributeID"],
                                        'arg1': row["arg1"],
                                        'arg2': row["arg2"]}

with bz2.BZ2File(args.expressionDumpPath, 'wb') as f:
    f.write(json.dumps(expressions).encode('utf-8'))

print("dumping effects")

effects = {}
for row in conn.execute('SELECT * FROM dgmeffects'):
    effects[row["effectID"]] = {'preExpression' : row["preExpression"],
                                'postExpression' : row["postExpression"],
                                'isOffensive': bool(row["isOffensive"]),
                                'isAssistance' : bool(row["isAssistance"])}

with bz2.BZ2File(args.effectDumpPath, 'wb') as f:
    f.write(json.dumps(effects).encode('utf-8'))

print("dumping done in " + str(time.clock() - start))
