#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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


from eos.util.cachedProperty import cachedproperty


class Expression:
    """
    Each effect, besides few metadata fields, contains two references to expressions
    (roots of expression tree), which actually describe how effect should affect other items.
    """

    def __init__(self, cacheHandler=None, expressionId=None, operandId=None,
                 arg1Id=None, arg2Id=None, value=None, expressionTypeId=None,
                 expressionGroupId=None, expressionAttributeId=None):
        # Cache handler which was used to build this expression
        self._cacheHandler = cacheHandler

        # Unique ID of expression
        self.id = expressionId

        # Operand of expression, field which each expression must have.
        # Describes actual effect of expression
        self.operandId = operandId

        # Value of expression, contains string or integer (in form of string)
        self.value = value

        # Arg attributes contain references to child expressions
        self._arg1Id = arg1Id
        self._arg2Id = arg2Id

        # References to type/group/attribute via integer ID
        self.expressionTypeId = expressionTypeId
        self.expressionGroupId = expressionGroupId
        self.expressionAttributeId = expressionAttributeId


    @cachedproperty
    def arg1(self):
        """
        First child expression.

        Possible exceptions:
        ExpressionFetchError -- raised when cache handler fails
        to fetch expression
        """
        if self._arg1Id is None:
            return None
        expression = self._cacheHandler.getExpression(self._arg1Id)
        return expression

    @cachedproperty
    def arg2(self):
        """
        Second child expression.

        Possible exceptions:
        ExpressionFetchError -- raised when cache handler fails
        to fetch expression
        """
        if self._arg2Id is None:
            return None
        expression = self._cacheHandler.getExpression(self._arg2Id)
        return expression
