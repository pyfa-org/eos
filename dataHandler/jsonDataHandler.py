'''
Created on 9-nov.-2011

@author: cncfanatics
'''
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
        if(not id):
            return None

        type = self.__typesCache.get(id)
        if(type == None):
            # We do str(id) here because json dicts always have strings as key
            data = self.__typeData[str(id)]
            type = Type(id, data["group"],
                        [self.getEffect(effectId) for effectId in data["effects"]],
                        {x : y for x, y in data["attributes"]})

            self.__typesCache[id] = type

        return type;

    def getExpression(self, id):
        if(not id):
            return None

        expression = self.__expressionsCache.get(id)
        if(expression == None):
            data = self.__expressionData[str(id)]
            expression = Expression(id, data["operand"], data["value"],
                                    [self.getExpression(expressionId) for expressionId in data["args"]],
                                    data["typeID"], data["groupID"], data["attributeID"])

            self.__expressionsCache[id] = expression

        return expression

    def getEffect(self, id):
        if(not id):
            return None

        effect = self.__effectsCache.get(id)
        if(effect == None):
            data = self.__effectData[str(id)]
            effect = Effect(id, self.getExpression(data["preExpression"]),
                            self.getExpression(data["postExpression"]),
                            data["isOffensive"], data["isAssistance"])

            self.__effectsCache[id] = effect

        return effect
