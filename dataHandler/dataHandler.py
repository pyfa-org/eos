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
        '''
        return the expression with the passed id
        '''
        ...

    @abstractmethod
    def getType(self, id):
        '''
        Return the type with the passed id
        '''
        ...

    @abstractmethod
    def getEffect(self, id):
        '''
        return the effect with the passed id
        '''
        ...