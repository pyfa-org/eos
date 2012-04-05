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


from eos.dataHandler.exception import ExpressionFetchError


class DataHandler:

    def __init__(self):
        self.__expressionData = {}

    def addExpressions(self, expressions):
        for expression in expressions:
            if expression.id in self.__expressionData:
                raise KeyError(expression.id)
            self.__expressionData[expression.id] = expression

    def getExpression(self, expId):
        try:
            expression = self.__expressionData[expId]
        except KeyError:
            raise ExpressionFetchError(expId)
        return expression


