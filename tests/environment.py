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

from eos.dataHandler.exception import TypeFetchError, AttributeFetchError, EffectFetchError, ExpressionFetchError
from eos.eve.attribute import Attribute
from eos.eve.effect import Effect
from eos.eve.expression import Expression
from eos.eve.type import Type


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
        self.__typeData = {}
        self.__attributeData = {}
        self.__effectData = {}
        self.__expressionData = {}

    def type_(self, **kwargs):
        if "dataHandler" in kwargs:
            raise TypeError("dataHandler")
        typ = Type(dataHandler=self, **kwargs)
        if typ.id in self.__typeData:
            raise KeyError(typ.id)
        self.__typeData[typ.id] = typ
        return typ

    def attribute(self, **kwargs):
        if "dataHandler" in kwargs:
            raise TypeError("dataHandler")
        attr = Attribute(dataHandler=self, **kwargs)
        if attr.id in self.__attributeData:
            raise KeyError(attr.id)
        self.__attributeData[attr.id] = attr
        return attr


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

    def getType(self, typeId):
        try:
            return self.__typeData[typeId]
        except KeyError:
            raise TypeFetchError(typeId)

    def getAttribute(self, attrId):
        try:
            return self.__attributeData[attrId]
        except KeyError:
            raise AttributeFetchError(attrId)

    def getEffect(self, effId):
        try:
            return self.__effectData[effId]
        except KeyError:
            raise EffectFetchError(effId)

    def getExpression(self, expId):
        try:
            return self.__expressionData[expId]
        except KeyError:
            raise ExpressionFetchError(expId)
