'''
Created on 11-nov.-2011

@author: cncfanatics
'''
class Expression(object):
    def __init__(self, dataHandler, id, operand, value, args, typeId=0, groupId=0, attributeId=0):
        self.dataHandler = dataHandler
        self.id = id
        self.operand = operand
        self.value = value
        self.args = args
        self.typeId = typeId
        self.groupId = groupId
        self.attributeId = attributeId