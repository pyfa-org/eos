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
Ugly script which outputs all expressions used by given effect, with details.
'''

import sqlite3

effectName = 'mining'
missing = {73, 74}

conn = sqlite3.connect("/home/dfx/Desktop/evechaos.db")
c = conn.cursor()

c.execute("SELECT preExpression, postExpression FROM dgmeffects WHERE effectName = ?", (effectName,))
for row in c:
    pre = row[0]
    post = row[1]

print("===== Effect {}, pre-expression =====\n".format(effectName))

opids = set()
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
            opids.add(row[1])
        checked.add(eID)
    checknext.difference_update(checked)
    tocheck = checknext
print("Used operandIDs: {}".format(", ".join(str(opid) for opid in sorted(opids))))
print("Undescribed operandIDs: {}\n".format(", ".join(str(opid) for opid in sorted(opids.intersection(missing)))))

print("===== Effect {}, post-expression =====\n".format(effectName))

opids = set()
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
            opids.add(row[1])
        checked.add(eID)
    checknext.difference_update(checked)
    tocheck = checknext
print("Used operandIDs: {}".format(", ".join(str(opid) for opid in sorted(opids))))
print("Undescribed operandIDs: {}\n".format(", ".join(str(opid) for opid in sorted(opids.intersection(missing)))))
