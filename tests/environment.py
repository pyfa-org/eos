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


from logging import getLogger, ERROR, WARNING

from eos.dataHandler.exception import EffectFetchError, ExpressionFetchError
from eos.eve.effect import Effect
from eos.eve.expression import Expression


class Logger:

    def __init__(self):
        self.__knownSignatures = set()
        self.__rootLogger = getLogger("eos_test")

    ERROR = ERROR
    WARNING = WARNING

    def warning(self, msg, childName=None, signature=None):
        logger = self.__getChildLogger(childName)
        if signature is None:
            logger.warning(msg)
        elif not signature in self.__knownSignatures:
            logger.warning(msg)
            self.__knownSignatures.add(signature)

    def error(self, msg, childName=None, signature=None):
        logger = self.__getChildLogger(childName)
        if signature is None:
            logger.error(msg)
        elif not signature in self.__knownSignatures:
            logger.error(msg)
            self.__knownSignatures.add(signature)

    def __getChildLogger(self, childName):
        if childName is None:
            logger = self.__rootLogger
        else:
            logger = self.__rootLogger.getChild(childName)
        return logger


class DataHandler:

    def __init__(self):
        self.__effectData = {}
        self.__expressionData = {}

    def effect(self, **kwargs):
        if "dataHandler" in kwargs:
            raise TypeError("dataHandler")
        eff = Effect(dataHandler=self, **kwargs)
        if eff.id in self.__effectData:
            raise KeyError(eff.id)
        self.__effectData[eff.id] = eff
        return eff

    def expression(self, **kwargs):
        if "dataHandler" in kwargs:
            raise TypeError("dataHandler")
        exp = Expression(dataHandler=self, **kwargs)
        if exp.id in self.__expressionData:
            raise KeyError(exp.id)
        self.__expressionData[exp.id] = exp
        return exp

    def getEffect(self, effId):
        try:
            effect = self.__effectData[effId]
        except KeyError:
            raise EffectFetchError(effId)
        return effect

    def getExpression(self, expId):
        try:
            expression = self.__expressionData[expId]
        except KeyError:
            raise ExpressionFetchError(expId)
        return expression
