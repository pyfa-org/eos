#===============================================================================
# Copyright (C) 2011 Diego Duclos
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

from .dataHandler import DataHandler
import json
import bz2
import weakref
from ..data import Type, Expression, Effect

class JsonDataHandler(DataHandler):
    '''
    JSON based dataHandler, this dataHandler will load eve staticdata and expression data into memory at instanciation from json files.
    Any call to getType or getExpression will be answered using the in-memory dictionaries.
    By default, files are assumed to be ./eos/data/eve.json.bz2 and ./eos/data/expressions.json.bz2
    Data is assumed to be encoded as UTF-8
    '''
    def __init__(self, typesPath, expressionsPath, effectsPath, encoding='utf-8'):
        self.__typesCache = weakref.WeakValueDictionary()
        self.__expressionsCache = weakref.WeakValueDictionary()
        self.__effectsCache = weakref.WeakValueDictionary()

        with bz2.BZ2File(typesPath, 'r') as f:
            self.__typeData = json.loads(f.read().decode('utf-8'))

        with bz2.BZ2File(expressionsPath, 'r') as f:
            self.__expressionData = json.loads(f.read().decode('utf-8'))

        with bz2.BZ2File(effectsPath, 'r') as f:
            self.__effectData = json.loads(f.read().decode('utf-8'))

    def getType(self, id):
        if not id:
            return None

        type = self.__typesCache.get(id)
        if type is None:
            # We do str(id) here because json dicts always have strings as key
            data = self.__typeData[str(id)]
            type = Type(id, data["group"],
                        [self.getEffect(effectId) for effectId in data["effects"]],
                        {x : y for x, y in data["attributes"]})

            self.__typesCache[id] = type

        return type;

    def getExpression(self, id):
        if not id:
            return None

        expression = self.__expressionsCache.get(id)
        if expression is None:
            data = self.__expressionData[str(id)]
            expression = Expression(id, data["operand"], data["value"],
                                    self.getExpression(data["arg1"]), self.getExpression(data["arg2"]),
                                    data["typeID"], data["groupID"], data["attributeID"])

            self.__expressionsCache[id] = expression

        return expression

    def getEffect(self, id):
        if not id:
            return None

        effect = self.__effectsCache.get(id)
        if effect is None:
            data = self.__effectData[str(id)]
            effect = Effect(id, self.getExpression(data["preExpression"]),
                            self.getExpression(data["postExpression"]),
                            data["isOffensive"], data["isAssistance"])

            self.__effectsCache[id] = effect

        return effect
