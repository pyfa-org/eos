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

import collections

class Expression(object):
    '''
    Expression class. Each effect is made out of several expressions. Which in turn, can be made out of expressions themselves.
    This class is typically reused by the dataHandler if the same id is requested multiple times.
    As such, there shouldn't be ANY fit-specific data on it.
    All info in this object is taken straight from EVE's cache.
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
        self._info = None

    def run(self, owner, fit):
        '''
        Run the effect against the passed owner and fit.
        The owner is the MutableAttributeHolder which will be used to apply/get source values
        Target values will be applied to the passed Fit object according to configured filters and other settings
        See ExpressionInfo for detailed workings
        '''
        if(self._infoList == None):
            self._info = ExpressionEval()
            self._info.build(self)

        self._info._run(owner, fit)

    def undo(self, owner, fit):
        '''
        Apply the reverse operation that was applied when run was called.
        run fills up a number of registers to make this operation possible
        '''
        # No check if __info is defined,
        # if the expression is being undo'd, it has to have been applied before anyway
        self._info._undo(owner, fit)

class ExpressionEval(object):
    '''
    Expression evaluator responsible for converting a tree of Expression objects (which isn't directly useful to us)
    into one or several ExpressionInfo objects which can then be ran as needed.
    '''
    def __init__(self):
        self.__activeExpression = None
        self.expressions = []

    def _run(self, owner, fit):
        '''
        Internal run method that applies all expressions stored in this eval object.
        This is typically called for you by the expression itself
        '''
        for e in self.expressions:
            e._run()

    def _undo(self, owner, fit):
        for e in self.expressions:
            e._undo()

    def build(self, base):
        '''
        Prepare an ExpressionEval object for running.
        No validations are done here, what is passed should be valid.
        If its not, exceptions will most likely occur, or you'll get an incomplete ExpressionInfo object as a result
        If this is not called before run()/undo() they will not do anything
        '''
        self.__build(base)
        return self.expressions

    def __build(self, element):
        '''
        Internal recursive building method.
        The public build() passes the base to this method, which will then proceed to build it, as well as all its children
        into (hopefully) fully functional ExpressionInfo objects.
        '''
        # Sanity guard
        if element is None:
            return

        # Get some stuff locally, we refer them often
        activeExpression = self.__activeExpression

        if element.operand == 17: #Splicing operator

            # If we already have an active expression, store it first.
            # This should be when a splicer is found somewhere down a tree,
            # I doubt this happens in practice ? It makes little sense
            if activeExpression is not None:
                self.expressions.append(self.__activeExpression)

            # Build first expression
            self.__activeExpression = ExpressionInfo()
            self.__build(element.arg1)
            self.expressions.append(self.__activeExpression)

            # Build second
            self.__activeExpression = ExpressionInfo()
            self.__build(element.arg2)
            self.expressions.append(self.__activeExpression)

            # Done
            return

        elif activeExpression is None:
            self.__activeExpression = activeExpression = ExpressionInfo()
            self.expressions.append(activeExpression)

        res1 = self.__build(element.arg1)
        res2 = self.__build(element.arg2)

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
            activeExpression.filters.append(ExpressionFilter("group", res2))
            return res1 #Entity, handled by parent

        elif element.operand == 49: #JoinSkillFilter
            activeExpression.filters.append(ExpressionFilter("skill", res2))
            return res1 #Entity, handled by parent


class ExpressionInfo(object):
    '''
    The ExpressionInfo objects are the actual "Core" of eos,
    they are what eventually applies an effect onto a fit.
    Which causes modules to actualy do useful(tm) things.
    They are typically generated by the ExpressionBuild class
    but nothing prevents a user from making some of his own and running them onto a fit
    '''
    def __init__(self):
        self.filters = []
        '''
        List of ExpressionFilter objects, each describing a single filter. ALL filters must be matched before anything is done
        '''

        self.operation = None
        '''
        Which operation should be applied.
        Possible values: <None implemented yet, getting to that :)>
        Any other values will be ignored, causing the ExpressionInfo to do nothing
        '''
        self.target = None
        '''
        The target of this expression.
        Possible values: <None implemented yet, getting to that :)>
        Any other values will be ignored, causing the ExpressionInfo to do nothing
        '''
        self.targetAttributeId = None
        '''
        Which attribute will be affected by the operation on the target.
        This will be used as dictionary lookup key on all matched targets (if any)
        '''

        self.sourceAttributeId = None
        '''
        Which source attribute will be used as calculation base for the operation.
        This will be used as dictionary lookup key on the owner passed to the run method
        '''

    def _run(self, owner, fit):
        '''
        Runner, applies this expression onto the passed fit using the passed owner.
        This is typically called for you by the ExpressionEval, unless you're running custom ExpressionInfo objects
        '''
        pass

    def _undo(self, owner, fit):
        '''
        Undos the operations applied by _run, usualy also called by the ExpressionEval that owns this ExpressionInfo.
        Unless you're running custom ExpressionInfo objects, you will usualy never call this
        '''
        pass

# A namedtuple was picked for this instead of a regular tuple to keep the meaning of each variable clear when they're called from code
# Also so we could eventually replace this with a full featured class if need be
ExpressionFilter = collections.namedtuple("ExpressionFilter", ('filterType', 'filterValue'))
'''
ExpressionFilter namedTuple, keeps track of filterType and filterValue.
'''