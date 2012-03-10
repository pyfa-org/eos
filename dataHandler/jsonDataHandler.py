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


from bz2 import BZ2File
from json import loads
from weakref import WeakValueDictionary

from eos.eve.const import nulls
from eos.eve.type import Type
from eos.eve.expression import Expression
from eos.eve.effect import Effect
from eos.eve.attribute import Attribute
from eos.util.callableData import CallableData
from .dataHandler import DataHandler
from .exception import TypeFetchError, AttributeFetchError, EffectFetchError, ExpressionFetchError


class JsonDataHandler(DataHandler):
    """
    JSON based dataHandler, this dataHandler will load eve staticdata and expression data into memory at instanciation from json files.
    Any call to getType or getExpression will be answered using the in-memory dictionaries.
    By default, files are assumed to be ./eos/data/eve.json.bz2 and ./eos/data/expressions.json.bz2
    Data is assumed to be encoded as UTF-8
    """
    def __init__(self, typesPath, attributesPath, effectsPath, expressionsPath, encoding="utf-8"):
        # Read JSON into data storage
        with BZ2File(typesPath, "r") as f:
            self.__typeData = loads(f.read().decode(encoding))
        with BZ2File(attributesPath, "r") as f:
            self.__attributeData = loads(f.read().decode(encoding))
        with BZ2File(effectsPath, "r") as f:
            self.__effectData = loads(f.read().decode(encoding))
        with BZ2File(expressionsPath, "r") as f:
            self.__expressionData = loads(f.read().decode(encoding))

        # Weakref cache for objects composed out of data from storage
        self.__typesCache = WeakValueDictionary()
        self.__attributesCache = WeakValueDictionary()
        self.__effectsCache = WeakValueDictionary()
        self.__expressionsCache = WeakValueDictionary()

    def getType(self, typeId):
        if typeId in nulls:
            return None
        try:
            type_ = self.__typesCache[typeId]
        except KeyError:
            # We do str(int(id)) here because JSON dictionaries
            # always have strings as key
            jsonTypeId = str(int(typeId))
            try:
                data = self.__typeData[jsonTypeId]
            except KeyError as e:
                raise TypeFetchError(typeId) from e
            groupId, catId, duration, discharge, optimal, falloff, tracking, fittable, effectIds, attrIds = data
            type_ = Type(typeId,
                         groupId=groupId,
                         categoryId=catId,
                         durationAttributeId=duration,
                         dischargeAttributeId=discharge,
                         rangeAttributeId=optimal,
                         falloffAttributeId=falloff,
                         trackingSpeedAttributeId=tracking,
                         fittableNonSingleton=fittable,
                         attributes={attrId: attrVal for attrId, attrVal in attrIds},
                         effects=tuple(self.getEffect(effectId) for effectId in effectIds))
            self.__typesCache[typeId] = type_
        return type_

    def getAttribute(self, attrId):
        if attrId in nulls:
            return None
        try:
            attribute = self.__attributesCache[attrId]
        except KeyError:
            jsonAttrId = str(int(attrId))
            try:
                data = self.__attributeData[jsonAttrId]
            except KeyError as e:
                raise AttributeFetchError(attrId) from e
            maxAttributeId, defaultValue, highIsGood, stackable = data
            attribute = Attribute(attrId,
                                  maxAttributeId=maxAttributeId,
                                  defaultValue=defaultValue,
                                  highIsGood=highIsGood,
                                  stackable=stackable)
            self.__attributesCache[attrId] = attribute
        return attribute

    def getEffect(self, effectId):
        if effectId in nulls:
            return None
        try:
            effect = self.__effectsCache[effectId]
        except KeyError:
            jsonEffectId = str(int(effectId))
            try:
                data = self.__effectData[jsonEffectId]
            except KeyError as e:
                raise EffectFetchError(effectId) from e
            effCategoryId, isOffence, isAssist, fitChanceId, preExpId, postExpId = data
            preExpData = CallableData(callable=self.getExpression, args=(preExpId,), kwargs={})
            postExpData = CallableData(callable=self.getExpression, args=(postExpId,), kwargs={})
            effect = Effect(effectId,
                            categoryId=effCategoryId,
                            isOffensive=isOffence,
                            isAssistance=isAssist,
                            fittingUsageChanceAttributeID=fitChanceId,
                            preExpressionData=preExpData,
                            postExpressionData=postExpData)
            self.__effectsCache[effectId] = effect

        return effect

    def getExpression(self, expId):
        if expId in nulls:
            return None
        try:
            expression = self.__expressionsCache[expId]
        except KeyError:
            jsonExpId = str(int(expId))
            try:
                data = self.__expressionData[jsonExpId]
            except KeyError as e:
                raise ExpressionFetchError(expId) from e
            opndId, arg1Id, arg2Id, eVal, eTypeId, eGrpId, eAttrId = data
            expression = Expression(expId,
                                    opndId,
                                    arg1=self.getExpression(arg1Id),
                                    arg2=self.getExpression(arg2Id),
                                    value=eVal,
                                    expressionTypeId=eTypeId,
                                    expressionGroupId=eGrpId,
                                    expressionAttributeId=eAttrId)
            self.__expressionsCache[expId] = expression
        return expression
