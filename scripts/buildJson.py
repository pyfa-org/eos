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
This script takes a sqlite cache dump as input and outputs several JSON files as bz2 archive.
"""

import time
start = time.clock()

import argparse
import bz2
import json
import sqlite3

parser = argparse.ArgumentParser(description="This script takes a sqlite cache dump as input and outputs several JSON files as bz2 archive.")
parser.add_argument("dbPath", type=str, help="The path to the sqlite cache dump")
parser.add_argument("-e", "--types", type=str, dest="types", default="types.json.bz2")
parser.add_argument("-a", "--attributes", type=str, dest="attributes", default="attributes.json.bz2")
parser.add_argument("-f", "--effects", type=str, dest="effects", default="effects.json.bz2")
parser.add_argument("-x", "--expressions", type=str, dest="expressions", default="expressions.json.bz2")
args = parser.parse_args()

conn = sqlite3.connect(args.dbPath, detect_types=sqlite3.PARSE_COLNAMES | sqlite3.PARSE_DECLTYPES)
conn.row_factory = sqlite3.Row

print("dumping types")
types = {}
for typeRow in conn.execute("SELECT typeID, groupID FROM invtypes"):
    statement = "SELECT categoryID, fittableNonSingleton FROM invgroups WHERE groupID = ?"
    grpRow = conn.execute(statement, (typeRow["groupID"],)).fetchone()
    # Tuple with effectIDs assigned to type
    statement = "SELECT effectID FROM dgmtypeeffects WHERE typeID = ?"
    typeEffects = tuple(effectRow["effectID"] for effectRow in conn.execute(statement, (typeRow["typeID"],)))
    # Tuple with (attributeID, attributeValue) tuples assigned to type
    statement = "SELECT attributeID, value FROM dgmtypeattribs WHERE typeID = ?"
    typeAttrs = tuple((attrRow["attributeID"], attrRow["value"]) for attrRow in conn.execute(statement, (typeRow["typeID"],)))
    types[typeRow["typeID"]] = (typeRow["groupID"], grpRow["categoryID"], typeEffects, typeAttrs)
with bz2.BZ2File(args.types, "wb") as f:
    f.write(json.dumps(types).encode("utf-8"))

print("dumping attributes")
attributes = {}
for row in conn.execute("SELECT attributeID, highIsGood, stackable FROM dgmattribs"):
    attributes[row["attributeID"]] = (row["highIsGood"], row["stackable"])
with bz2.BZ2File(args.attributes, "wb") as f:
    f.write(json.dumps(attributes).encode("utf-8"))

print("dumping effects")
effects = {}
for row in conn.execute("SELECT effectID, isOffensive, isAssistance, preExpression, postExpression FROM dgmeffects"):
    effects[row["effectID"]] = (row["isOffensive"], row["isAssistance"],
                                row["preExpression"], row["postExpression"])
with bz2.BZ2File(args.effects, "wb") as f:
    f.write(json.dumps(effects).encode("utf-8"))

print("dumping expressions")
expressions = {}
statement = "SELECT expressionID, operandID, arg1, arg2, expressionValue, expressionTypeID, expressionGroupID, expressionAttributeID FROM dgmexpressions"
for row in conn.execute(statement):
    expressions[row["expressionID"]] = (row["operandID"], row["arg1"], row["arg2"],
                                        row["expressionValue"],row["expressionTypeID"],
                                        row["expressionGroupID"], row["expressionAttributeID"])
with bz2.BZ2File(args.expressions, "wb") as f:
    f.write(json.dumps(expressions).encode("utf-8"))

print("dumping done in {}".format(round(time.clock()-start, 2)))
