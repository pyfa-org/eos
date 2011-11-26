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

from .eval import ExpressionEval

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

    def build(self):
        '''
        Builds the info objects for this expression tree
        '''
        if(self._info is None):
            self._info = ExpressionEval()
            self._info.build(self)

    def prepare(self, owner, fit):
        '''
        Prepare the expression for execution
        '''
        self.build()
        self._info._prepare(owner, fit)

    def apply(self, owner, fit):
        '''
        Run the effect against the passed owner and fit.
        The owner is the MutableAttributeHolder which will be used to apply/get source values
        Target values will be applied to the passed Fit object according to configured filters and other settings
        See ExpressionInfo for detailed workings
        '''
        self.build()
        self._info._apply(owner, fit)

    def undo(self, owner, fit):
        '''
        Apply the reverse operation that was applied when run was called.
        run fills up a number of registers to make this operation possible
        '''
        # No check if __info is defined,
        # if the expression is being undo'd, it has to have been applied before anyway
        self._info._undo(owner, fit)