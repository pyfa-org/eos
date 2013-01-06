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


import bz2
import json
import os.path
from weakref import WeakValueDictionary

from eos.eve.type import Type
from eos.eve.expression import Expression
from eos.eve.effect import Effect
from eos.eve.attribute import Attribute
from .exception import TypeFetchError, AttributeFetchError, EffectFetchError, ExpressionFetchError


class JsonCacheHandler:
    """
    Each time Eos is initialized, it loads data from packed JSON
    (disk cache) into memory data cache, and uses it to instantiate
    objects, which are stored in in-memory weakref object cache.

    Positional arguments:
    diskCacheFolder -- folder where on-disk cache files are stored
    name -- unique indentifier of cache, e.g. Eos instance name
    """
    def __init__(self, diskCacheFolder, name):
        self._diskCacheFile = os.path.join(diskCacheFolder, '{}.json.bz2'.format(name))
        # Initialize memory data cache
        self.__typeDataCache = {}
        self.__attributeDataCache = {}
        self.__effectDataCache = {}
        self.__expressionDataCache = {}
        self.__fingerprint = None
        # Initialize weakref object cache
        self.__typeObjCache = WeakValueDictionary()
        self.__attributeObjCache = WeakValueDictionary()
        self.__effectObjCache = WeakValueDictionary()
        self.__expressionObjCache = WeakValueDictionary()

        # Read JSON into local variable
        try:
            with bz2.BZ2File(self._diskCacheFile, 'r') as file:
                jsonData = file.read().decode('utf-8')
                data = json.loads(jsonData)
        # If file doesn't exist, JSON load errors occur, or
        # anything else bad happens, do not load anything
        # and leave values as initialized
        except:
            pass
        # Load data into data cache, if no errors occurred
        # during JSON reading/parsing
        else:
            self.__updateMemCache(data)


    def getType(self, typeId):
        """
        Get Type object from data source.

        Positional arguments:
        typeId -- ID of type to get

        Return value:
        eve.type.Type object
        """
        try:
            type_ = self.__typeObjCache[typeId]
        except KeyError:
            # We do str(int(id)) here because JSON dictionaries
            # always have strings as key
            jsonTypeId = str(int(typeId))
            try:
                data = self.__typeDataCache[jsonTypeId]
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
            self.__typeObjCache[typeId] = type_
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
            attribute = self.__attributeObjCache[attrId]
        except KeyError:
            jsonAttrId = str(int(attrId))
            try:
                data = self.__attributeDataCache[jsonAttrId]
            except KeyError as e:
                raise AttributeFetchError(attrId) from e
            maxAttributeId, defaultValue, highIsGood, stackable = data
            attribute = Attribute(cacheHandler=self,
                                  attributeId=attrId,
                                  maxAttributeId=maxAttributeId,
                                  defaultValue=defaultValue,
                                  highIsGood=highIsGood,
                                  stackable=stackable)
            self.__attributeObjCache[attrId] = attribute
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
            effect = self.__effectObjCache[effectId]
        except KeyError:
            jsonEffectId = str(int(effectId))
            try:
                data = self.__effectDataCache[jsonEffectId]
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
            self.__effectObjCache[effectId] = effect
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
            expression = self.__expressionObjCache[expId]
        except KeyError:
            jsonExpId = str(int(expId))
            try:
                data = self.__expressionDataCache[jsonExpId]
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
            self.__expressionObjCache[expId] = expression
        return expression

    def getFingerprint(self):
        """
        Get disk cache fingerprint.
        """
        return self.__fingerprint

    def updateCache(self, data, fingerprint):
        """
        Updates on-disk and memory caches.

        Positional arguments:
        data -- dictionary with data to update
        fingerprint -- string with fingerprint
        """
        data['fingerprint'] = fingerprint
        # Update disk cache
        os.makedirs(os.path.dirname(self._diskCacheFile), mode=0o755, exist_ok=True)
        #with bz2.BZ2File(args.attributes, "wb") as f:
        #    f.write(json.dumps(attributes).encode("utf-8"))
        with bz2.BZ2File(self._diskCacheFile, 'w') as file:
            jsonData = json.dumps(data).encode('utf-8')
            file.write(jsonData)
        # Update data cache
        self.__updateMemCache(data)


    def __updateMemCache(self, data):
        """
        Loads data into memory data cache.

        Positional arguments:
        data -- dictionary with data to load
        """
        self.__typeDataCache = data['types']
        self.__attributeDataCache = data['attributes']
        self.__effectDataCache = data['effects']
        self.__expressionDataCache = data['expressions']
        self.__fingerprint = data['fingerprint']
        # Also clear object cache to make sure objects composed
        # from old data are gone
        self.__typeObjCache.clear()
        self.__attributeObjCache.clear()
        self.__effectObjCache.clear()
        self.__expressionDataCache.clear()
