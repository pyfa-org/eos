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

class Expression(object):
    '''
    Expression class. Each effect is made out of several expressions. Which in turn, can be made out of expressions themselves.
    This class is typically reused by the dataHandler if the same id is requested multiple times.
    As such, there shouldn't be ANY fit-specific data on it
    '''

    def __init__(self, id, operand, value, arg1, arg2, typeId=0, groupId=0, attributeId=0):
        self.id = id
        self.operand = operand
        self.value = value
        self.arg1 = arg1
        self.arg2 = arg2
        self.typeId = typeId
        self.groupId = groupId
        self.attributeId = attributeId
        self.code = None

    def run(self, fit):
        if(self.code == None):
            builder = ExpressionBuild(self)
            self.code = builder.run()

class ExpressionBuild(object):
    def __init__(self, base):
        self.base = base
        self.activeExpression = None
        self.expressions = []

    def run(self):
        return self.build(self.base)

    def build(self, element):
        # Sanity guard
        if element is None:
            return

        # Get some stuff locally, we refer them often
        activeExpression = self.activeExpression

        if element.operand == 17: #Splicing operator

            # If we already have an active expression, store it first.
            # This should be when a splicer is found somewhere down a tree,
            # I doubt this happens in practice ? It makes little sense
            if activeExpression is not None:
                self.expressions.append(self.activeExpression)

            # Build first expression
            self.activeExpression = ExpressionInfo()
            self.build(element.arg1)
            self.expressions.append(self.activeExpression)

            # Build second
            self.activeExpression = ExpressionInfo()
            self.build(element.arg2)
            self.expressions.append(self.activeExpression)

            # Done
            return

        elif activeExpression is None:
            self.activeExpression = activeExpression = ExpressionInfo()
            self.expressions.append(activeExpression)

        res1 = self.build(element.arg1)
        res2 = self.build(element.arg2)

        if element.operand in (6, 7): #6: AddItemModifier #7: AddItemModifierGroupFilter
            activeExpression.sourceAttributeId = res2

        elif element.operand == 12: #12: joinEntityAndAttribute
            return (res1, #Entity
                    res2) #Attribute

        elif element.operand in (21, 24, 26, 29): #21: Operand #24: Entity #26: Group
            return element.value

        elif element.operand == 22: #22: attributeId
            return element.attributeId

        elif element.operand == 31: #JoinEntityAttributeAndOperation
            activeExpression.operation = res1
            activeExpression.target, activeExpression.targetAttributeId = res2

        elif element.operand == 48: #JoinGroupFilter
            activeExpression.filters.append(("group", res2))
            return res1 #Entity, handled by parent

        elif element.operand == 49: #JoinSkillFilter
            activeExpression.filters.append(("skill", res2))
            return res1 #Entity, handled by parent


class ExpressionInfo(object):
    def __init__(self):
        self.filters = []
        self.operation = None
        self.target = None
        self.targetAttributeId = None
        self.sourceAttributeId = None
