'''
Created on 11-nov.-2011

@author: cncfanatics
'''
class Type(object):
    def __init__(self, dataHandler, id, groupId, effects, attributes):
        self.dataHandler = dataHandler
        self.id = id
        self.groupId = groupId
        self.effects = effects
        self.attributes = attributes