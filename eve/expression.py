#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2012 Anton Vorobyov
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


class Expression:
    """
    Each effect, besides few metadata fields, contains two references to expressions
    (roots of expression tree), which actually describe how effect should affect other items.
    """

    def __init__(self, id_, operandId, arg1=None, arg2=None, value=None,
                 expressionTypeId=None, expressionGroupId=None, expressionAttributeId=None):
        # Unique ID of expression
        self.id = id_

        # Operand of expression, field which each expression must have.
        # Describes actual effect of expression
        self.operandId = operandId

        # Value of expression, contains string or integer (in form of string)
        self.value = value

        # Arg attributes contain references to child expressions
        self.arg1 = arg1
        self.arg2 = arg2

        # References to type/group/attribute via integer ID
        self.expressionTypeId = expressionTypeId
        self.expressionGroupId = expressionGroupId
        self.expressionAttributeId = expressionAttributeId
