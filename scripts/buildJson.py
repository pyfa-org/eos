'''
buildJson.py script.
This script takes a sqlite cache dump as input and outputs two bz2 compressed json files. One for eve staticdata (invtypes, invtypeattribs, invtypeeffects) and another for expression data.
'''

import time
start = time.clock()

import argparse
import sqlite3
import json
import bz2

parser = argparse.ArgumentParser(description="This script takes a sqlite cache dump as input and outputs two bz2 compressed json files. One for eve staticdata (invtypes, invtypeattribs, invtypeeffects) and another for expression data.")
parser.add_argument("dbPath", type=str, help="The path to the sqlite cache dump")
parser.add_argument("-e", "--typedump", dest="typeDumpPath", default="types.json.bz2")
parser.add_argument("-x", "--expressiondump", dest="expressionDumpPath", default="expressions.json.bz2")
parser.add_argument("-f", "--effectDump", dest="effectDumpPath", default="effects.json.bz2")
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
                                        'args': (row["arg1"], row["arg2"])}

with bz2.BZ2File(args.expressionDumpPath, 'wb') as f:
    f.write(json.dumps(expressions).encode('utf-8'))

print("dumping effects")

effects = {}
for row in conn.execute('SELECT * FROM dgmeffects'):
    effects[row["effectID"]] = {'preExpression' : row["preExpression"],
                                'postExpression' : row["postExpression"],
                                'isOffensive': row["isOffensive"],
                                'isAssistance' : row["isAssistance"]}

with bz2.BZ2File(args.effectDumpPath, 'wb') as f:
    f.write(json.dumps(effects).encode('utf-8'))

print("dumping done in " + str(time.clock() - start))