'''
Created on 9-nov.-2011

@author: cncfanatics
'''

from abc import ABCMeta
from abc import abstractmethod

class DataHandler(object):
    '''
    DataHandler abstract baseclass, it handles fetching relevant data from wherever it is stored
    '''
    __metaclass__ = ABCMeta

    @abstractmethod
    def getExpression(self, id):
        ...

    @abstractmethod
    def getType(self, id):
        ...

    @abstractmethod
    def getEffect(self, id):
        ...