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

from eos.eve.invType import InvType
from eos.eve.expression import Expression
from eos.eve.effect import Effect
from eos.eve.attribute import Attribute
from .dataHandler import DataHandler


nulls = {0, None}


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
            invType = self.__typesCache[typeId]
        except KeyError:
            # We do str(int(id)) here because JSON dictionaries
            # always have strings as key
            data = self.__typeData[str(int(typeId))]
            groupId, catId, fittableNS, effectIds, attrIds = data
            invType = InvType(typeId, groupId=groupId, categoryId=catId, fittableNonSingleton=fittableNS,
                              attributes={attrId: attrVal for attrId, attrVal in attrIds},
                              effects={self.getEffect(effectId) for effectId in effectIds})
            self.__typesCache[typeId] = invType
        return invType

    def getAttribute(self, attrId):
        if attrId in nulls:
            return None
        try:
            attribute = self.__attributesCache[attrId]
        except KeyError:
            data = self.__attributeData[str(int(attrId))]
            highIsGood, stackable = data
            attribute = Attribute(attrId, highIsGood=highIsGood, stackable=stackable)
            self.__attributesCache[attrId] = attribute
        return attribute

    def getEffect(self, effectId):
        if effectId in nulls:
            return None
        try:
            effect = self.__effectsCache[effectId]
        except KeyError:
            data = self.__effectData[str(int(effectId))]
            isOffence, isAssist, preExpId, postExpId = data
            effect = Effect(effectId, isOffensive=isOffence, isAssistance=isAssist,
                            preExpression=self.getExpression(preExpId),
                            postExpression=self.getExpression(postExpId))
            self.__effectsCache[effectId] = effect

        return effect

    def getExpression(self, expId):
        if expId in nulls:
            return None
        try:
            expression = self.__expressionsCache[expId]
        except KeyError:
            data = self.__expressionData[str(int(expId))]
            opndId, arg1Id, arg2Id, eVal, eTypeId, eGrpId, eAttrId = data
            expression = Expression(opndId, arg1=self.getExpression(arg1Id),
                                    arg2=self.getExpression(arg2Id), value=eVal,
                                    typeId=eTypeId, groupId=eGrpId, attributeId=eAttrId)
            self.__expressionsCache[expId] = expression
        return expression
