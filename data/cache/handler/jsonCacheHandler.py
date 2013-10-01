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

from eos.data.cache.handler import CacheHandler
from eos.data.cache.object import *
from .exception import TypeFetchError, AttributeFetchError, EffectFetchError, ModifierFetchError


class JsonCacheHandler(CacheHandler):
    """
    This cache handler implements on-disk cache store in the form
    of compressed JSON. To improve performance further, it also
    keeps loads data from on-disk cache to memory, and uses weakref
    object cache for assembled objects.

    Positional arguments:
    diskCacheFolder -- folder where on-disk cache files are stored
    name -- unique indentifier of cache, e.g. Eos instance name
    logger -- logger to use for errors
    """

    def __init__(self, diskCacheFolder, name, logger):
        self._diskCacheFile = os.path.join(diskCacheFolder, '{}.json.bz2'.format(name))
        self._logger = logger
        # Initialize memory data cache
        self.__typeDataCache = {}
        self.__attributeDataCache = {}
        self.__effectDataCache = {}
        self.__modifierDataCache = {}
        self.__fingerprint = None
        # Initialize weakref object cache
        self.__typeObjCache = WeakValueDictionary()
        self.__attributeObjCache = WeakValueDictionary()
        self.__effectObjCache = WeakValueDictionary()
        self.__modifierObjCache = WeakValueDictionary()

        # If cache doesn't exist, silently finish initialization
        if not os.path.exists(self._diskCacheFile):
            return
        # Read JSON into local variable
        try:
            with bz2.BZ2File(self._diskCacheFile, 'r') as file:
                jsonData = file.read().decode('utf-8')
                data = json.loads(jsonData)
        except KeyboardInterrupt:
            raise
        # If file doesn't exist, JSON load errors occur, or
        # anything else bad happens, do not load anything
        # and leave values as initialized
        except:
            msg = 'error during reading cache'
            self._logger.error(msg, childName='cacheHandler')
        # Load data into data cache, if no errors occurred
        # during JSON reading/parsing
        else:
            self.__updateMemCache(data)

    def getType(self, typeId):
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
            groupId, catId, duration, discharge, optimal, falloff, tracking, fittable, effects, attribs = data
            type_ = Type(typeId=typeId,
                         groupId=groupId,
                         categoryId=catId,
                         durationAttributeId=duration,
                         dischargeAttributeId=discharge,
                         rangeAttributeId=optimal,
                         falloffAttributeId=falloff,
                         trackingSpeedAttributeId=tracking,
                         fittableNonSingleton=fittable,
                         attributes={attrId: attrVal for attrId, attrVal in attribs},
                         effects=tuple(self.getEffect(effectId) for effectId in effects))
            self.__typeObjCache[typeId] = type_
        return type_

    def getAttribute(self, attrId):
        try:
            attribute = self.__attributeObjCache[attrId]
        except KeyError:
            jsonAttrId = str(int(attrId))
            try:
                data = self.__attributeDataCache[jsonAttrId]
            except KeyError as e:
                raise AttributeFetchError(attrId) from e
            maxAttributeId, defaultValue, highIsGood, stackable = data
            attribute = Attribute(attributeId=attrId,
                                  maxAttributeId=maxAttributeId,
                                  defaultValue=defaultValue,
                                  highIsGood=highIsGood,
                                  stackable=stackable)
            self.__attributeObjCache[attrId] = attribute
        return attribute

    def getEffect(self, effectId):
        try:
            effect = self.__effectObjCache[effectId]
        except KeyError:
            jsonEffectId = str(int(effectId))
            try:
                data = self.__effectDataCache[jsonEffectId]
            except KeyError as e:
                raise EffectFetchError(effectId) from e
            effCategoryId, isOffence, isAssist, fitChanceId, buildStatus, modifiers = data
            effect = Effect(effectId=effectId,
                            categoryId=effCategoryId,
                            isOffensive=isOffence,
                            isAssistance=isAssist,
                            fittingUsageChanceAttributeId=fitChanceId,
                            buildStatus=buildStatus,
                            modifiers=tuple(self.getModifier(modifierId) for modifierId in modifiers))
            self.__effectObjCache[effectId] = effect
        return effect

    def getModifier(self, modifierId):
        try:
            modifier = self.__modifierObjCache[modifierId]
        except KeyError:
            jsonModifierId = str(int(modifierId))
            try:
                data = self.__modifierDataCache[jsonModifierId]
            except KeyError as e:
                raise ModifierFetchError(modifierId) from e
            state, context, srcAttrId, operator, tgtAttrId, location, filType, filValue = data
            modifier = Modifier(modifierId=modifierId,
                                state=state,
                                context=context,
                                sourceAttributeId=srcAttrId,
                                operator=operator,
                                targetAttributeId=tgtAttrId,
                                location=location,
                                filterType=filType,
                                filterValue=filValue)
            self.__modifierObjCache[modifierId] = modifier
        return modifier

    def getFingerprint(self):
        return self.__fingerprint

    def updateCache(self, data, fingerprint):
        # Make light version of data and add fingerprint
        # to it
        data = self.__stripData(data)
        data['fingerprint'] = fingerprint
        # Update disk cache
        cacheFolder = os.path.dirname(self._diskCacheFile)
        if not os.path.exists(cacheFolder):
            os.makedirs(cacheFolder, mode=0o755)
        with bz2.BZ2File(self._diskCacheFile, 'w') as file:
            jsonData = json.dumps(data)
            file.write(jsonData.encode('utf-8'))
        # Update data cache; encode to JSON and decode back
        # to make sure form of data is the same as after
        # loading it from cache (e.g. dictionary keys are
        # stored as strings in JSON)
        data = json.loads(jsonData)
        self.__updateMemCache(data)

    def __stripData(self, data):
        """
        Rework passed data, keying it and stripping dictionary
        keys from rows for performance.
        """
        slimData = {}

        slimTypes = {}
        for typeRow in data['types']:
            typeId = typeRow['typeId']
            slimTypes[typeId] = (typeRow['groupId'],
                                 typeRow['categoryId'],
                                 typeRow['durationAttributeId'],
                                 typeRow['dischargeAttributeId'],
                                 typeRow['rangeAttributeId'],
                                 typeRow['falloffAttributeId'],
                                 typeRow['trackingSpeedAttributeId'],
                                 typeRow['fittableNonSingleton'],
                                 tuple(typeRow['effects']),  # List -> tuple
                                 tuple(typeRow['attributes'].items()))  # Dictionary -> tuple
        slimData['types'] = slimTypes

        slimAttribs = {}
        for attrRow in data['attributes']:
            attrId = attrRow['attributeId']
            slimAttribs[attrId] = (attrRow['maxAttributeId'],
                                   attrRow['defaultValue'],
                                   attrRow['highIsGood'],
                                   attrRow['stackable'])
        slimData['attributes'] = slimAttribs

        slimEffects = {}
        for effectRow in data['effects']:
            effectId = effectRow['effectId']
            slimEffects[effectId] = (effectRow['effectCategory'],
                                     effectRow['isOffensive'],
                                     effectRow['isAssistance'],
                                     effectRow['fittingUsageChanceAttributeId'],
                                     effectRow['buildStatus'],
                                     tuple(effectRow['modifiers']))  # List -> tuple
        slimData['effects'] = slimEffects

        slimModifiers = {}
        for modifierRow in data['modifiers']:
            modifierId = modifierRow['modifierId']
            slimModifiers[modifierId] = (modifierRow['state'],
                                         modifierRow['context'],
                                         modifierRow['sourceAttributeId'],
                                         modifierRow['operator'],
                                         modifierRow['targetAttributeId'],
                                         modifierRow['location'],
                                         modifierRow['filterType'],
                                         modifierRow['filterValue'])
        slimData['modifiers'] = slimModifiers

        return slimData

    def __updateMemCache(self, data):
        """
        Loads data into memory data cache.

        Positional arguments:
        data -- dictionary with data to load
        """
        self.__typeDataCache = data['types']
        self.__attributeDataCache = data['attributes']
        self.__effectDataCache = data['effects']
        self.__modifierDataCache = data['modifiers']
        self.__fingerprint = data['fingerprint']
        # Also clear object cache to make sure objects composed
        # from old data are gone
        self.__typeObjCache.clear()
        self.__attributeObjCache.clear()
        self.__effectObjCache.clear()
        self.__modifierObjCache.clear()
