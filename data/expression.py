'''
Created on 11-nov.-2011

@author: cncfanatics
'''
class Expression(object):
    '''
    Expression class. Each effect is made out of several expressions. Which in turn, can be made out of expressions themselves.
    This class is typically reused by the dataHandler if the same id is requested multiple times.
    As such, there shouldn't be ANY fit-specific data on it
    '''

    def __init__(self, dataHandler, id, operand, value, args, typeId=0, groupId=0, attributeId=0):
        self.dataHandler = dataHandler
        self.id = id
        self.operand = operand
        self.value = value
        self.args = args
        self.typeId = typeId
        self.groupId = groupId
        self.attributeId = attributeId