'''
Created on 9-nov.-2011

@author: cncfanatics
'''
from .dataHandler import DataHandler
import json
import bz2
import weakref

class JsonDataHandler(DataHandler):
    '''
    JSON based dataHandler, this dataHandler will load eve staticdata and expression data into memory at instanciation from json files.
    Any call to getType or getExpression will be answered using the in-memory dictionaries.
    By default, files are assumed to be ./data/eve.json.bz2 and ./data/expressions.json.bz2
    Data is assumed to be encoded as UTF-8
    '''
    def __init__(self, evePath="./data/eve.json.bz2", expressionPath="./data/expressions.json.bz2", encoding='utf-8'):
        self.__typesCache = weakref.WeakValueDictionary()
        self.__expressionsCache = weakref.WeakValueDictionary()

        with bz2.BZ2File(evePath, 'r') as f:
            self.__eveData = json.loads(f.read().decode('utf-8'))

        with bz2.BZ2File(expressionPath, 'r') as f:
            self.__expressionData = json.loads(f.read().decode('utf-8'))

    def getType(self, id):
        '''
        Return the type with the passed id
        '''
        type = self.__typesCache.get(id)
        if(type == None):
            pass

        return type;

    def getExpression(self, id):
        '''
        return the expression with the passed id
        '''
        return self.__expressionData[str(id)];