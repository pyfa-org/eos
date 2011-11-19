#!/usr/bin/env python3
#===============================================================================
# Copyright (C) 2011 Anton Vorobyov
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

'''
Script which outputs all effects which use expressions with given operandID,
and all items with these effects.
'''

import argparse
import sqlite3
import sys

# Parse command line arguments
parser = argparse.ArgumentParser(description="This script takes given operandID and composes list of effects which use it")
parser.add_argument("-d", "--data", type=str)
parser.add_argument("-o", "--operand", type=int)
args = parser.parse_args()

# Check if  we got everything we need
if args.data is None or args.operand is None:
    sys.stderr.write("You must specify path to database and operandID\n")
    sys.exit()

# Connect to actual db
conn = sqlite3.connect(args.data)
c = conn.cursor()

# Set with IDs of expressions where requested operand is used, and IDs of their parents
parents = set()
# Auxiliary set, contains IDs of expressions we'll have to check next iteration
tocheck = set()
# Auxiliary set, contains IDs of expressions we already checked
checked = set()

# Get IDs of expressions where operand is directly used
c.execute("SELECT expressionID FROM dgmexpressions WHERE operandID = ?", (args.operand,))
for row in c:
    parents.add(row[0])
    tocheck.add(row[0])

# Go through all expression IDs we want to check
while(len(tocheck) > 0):
    # Set of expressions we'll probably check next cycle
    checknext = set()
    for eid in tocheck:
        # Mark current expression as checked
        checked.add(eid)
        # Get IDs of expressions which reference expression being checked as one of the arguments
        c.execute("SELECT expressionID FROM dgmexpressions WHERE arg1 = ? OR arg2 = ?", (eid, eid))
        for row in c:
            if row[0] not in parents:
                # Add all of them to list of parents and expressions we'll check next
                parents.add(row[0])
                checknext.add(row[0])
    # Next time, we'll check what we planned to check minus already checked expressions
    tocheck = checknext.difference(checked)

# Dictionary-container for effects which use our operand, and items which have these effects
effects = {}
# Cycle as long as we have something in parent set
while(len(parents) > 0):
    # To limit length of sql query, compose new set with 100 IDs
    newset = set()
    for i in range(min(100, len(parents))):
        newset.add(parents.pop())
    # Get effects with expressionIDs which use our operand
    c.execute("SELECT effectName FROM dgmeffects WHERE preExpression IN ({0}) OR postExpression IN ({0})".format(",".join("?" for i in newset)), (tuple(list(i for i in newset) + list(i for i in newset))))
    for row in c:
        effects[row[0]] = set()

# After, go through all effects and find items which use it
for en in effects:
    c.execute("SELECT it.typeName FROM invtypes AS it INNER JOIN dgmtypeeffects AS dte ON dte.typeID = it.typeID INNER JOIN dgmeffects AS de ON de.effectID = dte.effectID WHERE effectName = ?", (en,))
    for row in c:
        effects[en].add(row[0])

# Print jobs
for k in sorted(effects):
    v = effects[k]
    if len(v) > 100:
        print("Effect {} is used by > 100 of items".format(k))
    elif len(v) == 0:
        print("Effect {} is not used in any of items".format(k))
    else:
        print("Effect {} is used in items: {}".format(k, ", ".join(sorted(v))))
