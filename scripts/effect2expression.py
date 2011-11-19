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
Script which outputs all expressions used by given effect, with details.
'''

import argparse
import sqlite3
import sys

# Parse command line arguments
parser = argparse.ArgumentParser(description="This script outputs all expressions used by given effect, with details")
parser.add_argument("-d", "--data", type=str)
parser.add_argument("-e", "--effect", type=str)
args = parser.parse_args()

# Check if we got everything we need
if args.data is None or args.effect is None:
    sys.stderr.write("You must specify path to database and effect name\n")
    sys.exit()

# Connect to database
print(args.data)
conn = sqlite3.connect(args.data)
c = conn.cursor()

# Get pre- and post-expressions of given effect
c.execute("SELECT preExpression, postExpression FROM dgmeffects WHERE effectName = ?", (args.effect,))
for row in c:
    pre = row[0]
    post = row[1]

# Start pre-expression processing
print("===== Effect {}, pre-expression =====\n".format(args.effect))

# Cyclicly go through expressions and their arguments, printing data about them
tocheck = set()
tocheck.add(pre)
checked = set()
checked.add(0)
while(len(tocheck) > 0):
    checknext = set()
    for eID in tocheck:
        c.execute("SELECT expressionID, operandID, arg1, arg2, expressionValue, description, expressionName, expressionTypeID, expressionGroupID, expressionAttributeID FROM dgmexpressions WHERE expressionID = ?", (eID,))
        for row in c:
            print("Expression {}:\n  operandID: {}\n  arg1: {}\n  arg2: {}\n  expressionValue: {}\n  description: {}\n  expressionName: {}\n  expressionTypeID: {}\n  expressionGroupID: {}\n  expressionAttributeID: {}\n".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]))
            checknext.add(row[2])
            checknext.add(row[3])
        checked.add(eID)
    checknext.difference_update(checked)
    tocheck = checknext

# Same for post-expression
print("===== Effect {}, post-expression =====\n".format(args.effect))

tocheck = set()
tocheck.add(post)
checked = set()
checked.add(0)
while(len(tocheck) > 0):
    checknext = set()
    for eID in tocheck:
        c.execute("SELECT expressionID, operandID, arg1, arg2, expressionValue, description, expressionName, expressionTypeID, expressionGroupID, expressionAttributeID FROM dgmexpressions WHERE expressionID = ?", (eID,))
        for row in c:
            print("Expression {}:\n  operandID: {}\n  arg1: {}\n  arg2: {}\n  expressionValue: {}\n  description: {}\n  expressionName: {}\n  expressionTypeID: {}\n  expressionGroupID: {}\n  expressionAttributeID: {}\n".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]))
            checknext.add(row[2])
            checknext.add(row[3])
        checked.add(eID)
    checknext.difference_update(checked)
    tocheck = checknext
