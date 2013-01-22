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


class ExpressionFactory:

    def __init__(self):
        self._expressions = []

    def make(self, expressionId, operandId=None, arg1Id=None, arg2Id=None,
             expressionValue=None, expressionTypeId=None, expressionGroupId=None,
             expressionAttributeId=None):
        expRow = {'expressionId': expressionId, 'operandId': operandId, 'arg1Id': arg1Id, 'arg2Id': arg2Id,
                  'expressionValue': expressionValue, 'expressionTypeId': expressionTypeId,
                  'expressionGroupId': expressionGroupId, 'expressionAttributeId': expressionAttributeId}
        self._expressions.append(expRow)
        return expRow

    @property
    def data(self):
        return self._expressions


