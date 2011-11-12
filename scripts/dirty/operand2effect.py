import sqlite3

operandID = 74

conn = sqlite3.connect("/home/dfx/Desktop/evechaos.db")
c = conn.cursor()

parents = set()
tocheck = set()

c.execute("SELECT expressionID FROM dgmexpressions WHERE operandID = ?", (operandID,))
for row in c:
    parents.add(row[0])
    tocheck.add(row[0])

while(len(tocheck) > 0):
    checknext = set()
    for eid in tocheck:
        c.execute("SELECT expressionID FROM dgmexpressions WHERE arg1 = ? OR arg2 = ?", (eid, eid))
        for row in c:
            if row[0] not in parents:
                parents.add(row[0])
                checknext.add(row[0])
    tocheck = checknext

effects = {}
while(len(parents) > 0):
    newset = set()
    for i in range(min(100, len(parents))):
        newset.add(parents.pop())
    c.execute("SELECT effectName FROM dgmeffects WHERE preExpression IN ({0}) OR postExpression IN ({0})".format(",".join("?" for i in newset)), (tuple(list(i for i in newset) + list(i for i in newset))))
    for row in c:
        effects[row[0]] = set()

for en in effects:
    c.execute("SELECT it.typeName FROM invtypes AS it INNER JOIN dgmtypeeffects AS dte ON dte.typeID = it.typeID INNER JOIN dgmeffects AS de ON de.effectID = dte.effectID WHERE effectName = ?", (en,))
    for row in c:
        effects[en].add(row[0])

for k in sorted(effects):
    v = effects[k]
    if len(v) > 100:
        print("Effect {} is used in fuckton of items".format(k))
    elif len(v) == 0:
        print("Effect {} is not used in any of items".format(k))
    else:
        print("Effect {} is used in items: {}".format(k, ", ".join(sorted(v))))
