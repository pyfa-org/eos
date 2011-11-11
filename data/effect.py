'''
Created on 11-nov.-2011

@author: cncfanatics
'''
class Effect(object):
    '''
    Represents a single effect. Effects are the building blocks of types and are what actualy make a type do something.
    In turn, each effect is made out of pre- and a post-expression
    This class is typically reused by the dataHandler if the same id is requested multiple times.
    As such, there shouldn't be ANY fit-specific data on it
    '''

    def __init__(self, dataHandler, id, preExpression, postExpression, isOffensive, isAssistance):
        self.dataHandler = dataHandler
        self.id = id
        self.preExpression = preExpression
        self.postExpression = postExpression
        self.isOffensive = isOffensive
        self.isAssistance = isAssistance