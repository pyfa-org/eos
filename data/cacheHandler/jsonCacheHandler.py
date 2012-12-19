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


import bz2
import json
from weakref import WeakValueDictionary

from eos.eve.type import Type
from eos.eve.expression import Expression
from eos.eve.effect import Effect
from eos.eve.attribute import Attribute
from .exception import TypeFetchError, AttributeFetchError, EffectFetchError, ExpressionFetchError


class JsonCacheHandler:
    """
    Each time Eos is initialized, it loads data from packed JSON
    (disk cache) and instantiates appropriate objects using this
    class.
    """
    def __init__(self, dumpPath):
        # Read JSON into data storage
        with bz2.BZ2File(dumpPath, 'r') as file:
            self.__typeData = json.load(file)
        with bz2.BZ2File(dumpPath, 'r') as file:
            self.__attributeData = json.load(file)
        with bz2.BZ2File(dumpPath, 'r') as file:
            self.__effectData = json.load(file)
        with bz2.BZ2File(dumpPath, 'r') as file:
            self.__expressionData = json.load(file)

        # Weakref cache for objects composed out of data from storage
        self.__typesCache = WeakValueDictionary()
        self.__attributesCache = WeakValueDictionary()
        self.__effectsCache = WeakValueDictionary()
        self.__expressionsCache = WeakValueDictionary()

    def getType(self, typeId):
        """
        Get Type object from data source.

        Positional arguments:
        typeId -- ID of type to get

        Return value:
        eve.type.Type object
        """
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
            type_ = Type(cacheHandler=self,
                         typeId=typeId,
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
        """
        Get Attribute object from data source.

        Positional arguments:
        attrId -- ID of attribute to get

        Return value:
        eve.attribute.Attribute object
        """
        try:
            attribute = self.__attributesCache[attrId]
        except KeyError:
            jsonAttrId = str(int(attrId))
            try:
                data = self.__attributeData[jsonAttrId]
            except KeyError as e:
                raise AttributeFetchError(attrId) from e
            maxAttributeId, defaultValue, highIsGood, stackable = data
            attribute = Attribute(cacheHandler=self,
                                  attributeId=attrId,
                                  maxAttributeId=maxAttributeId,
                                  defaultValue=defaultValue,
                                  highIsGood=highIsGood,
                                  stackable=stackable)
            self.__attributesCache[attrId] = attribute
        return attribute

    def getEffect(self, effectId):
        """
        Get Effect object from data source.

        Positional arguments:
        effectId -- ID of effect to get

        Return value:
        eve.effect.Effect object
        """
        try:
            effect = self.__effectsCache[effectId]
        except KeyError:
            jsonEffectId = str(int(effectId))
            try:
                data = self.__effectData[jsonEffectId]
            except KeyError as e:
                raise EffectFetchError(effectId) from e
            effCategoryId, isOffence, isAssist, fitChanceId, preExpId, postExpId = data
            effect = Effect(cacheHandler=self,
                            effectId=effectId,
                            categoryId=effCategoryId,
                            isOffensive=isOffence,
                            isAssistance=isAssist,
                            fittingUsageChanceAttributeId=fitChanceId,
                            preExpressionId=preExpId,
                            postExpressionId=postExpId)
            self.__effectsCache[effectId] = effect
        return effect

    def getExpression(self, expId):
        """
        Get Expression object from data source.

        Positional arguments:
        expId -- ID of expression to get

        Return value:
        eve.expression.Expression object
        """
        try:
            expression = self.__expressionsCache[expId]
        except KeyError:
            jsonExpId = str(int(expId))
            try:
                data = self.__expressionData[jsonExpId]
            except KeyError as e:
                raise ExpressionFetchError(expId) from e
            opndId, arg1Id, arg2Id, eVal, eTypeId, eGrpId, eAttrId = data
            expression = Expression(cacheHandler=self,
                                    expressionId=expId,
                                    operandId=opndId,
                                    arg1Id=arg1Id,
                                    arg2Id=arg2Id,
                                    value=eVal,
                                    expressionTypeId=eTypeId,
                                    expressionGroupId=eGrpId,
                                    expressionAttributeId=eAttrId)
            self.__expressionsCache[expId] = expression
        return expression
