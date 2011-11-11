'''
Created on 11-nov.-2011

@author: cncfanatics
'''
class Type(object):
    '''
    A type, the basic building blocks of EVE. Everything that can do something is a type.
    Each type is built out of several effects and attributes.
    This class is typically reused by the dataHandler if the same id is requested multiple times.
    As such, there shouldn't be ANY fit-specific data on it
    '''
    def __init__(self, dataHandler, id, groupId, effects, attributes):
        self.dataHandler = dataHandler
        self.id = id
        self.groupId = groupId
        self.effects = effects
        self.attributes = attributes