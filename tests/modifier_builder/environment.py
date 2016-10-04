# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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
# ===============================================================================


class ExpressionFactory:

    def __init__(self):
        self._expressions = []

    def make(
            self,
            expressionID,
            operandID=None,
            arg1=None,
            arg2=None,
            expressionValue=None,
            expressionTypeID=None,
            expressionGroupID=None,
            expressionAttributeID=None
    ):
        exp_row = {
            'expressionID': expressionID, 'operandID': operandID, 'arg1': arg1, 'arg2': arg2,
            'expressionValue': expressionValue, 'expressionTypeID': expressionTypeID,
            'expressionGroupID': expressionGroupID, 'expressionAttributeID': expressionAttributeID
        }
        self._expressions.append(exp_row)
        return exp_row

    @property
    def data(self):
        return self._expressions


