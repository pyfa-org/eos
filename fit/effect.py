'''
Created on 11-nov.-2011

@author: cncfanatics
'''
class Effect(object):
    def __init__(self, dataHandler, id, preExpression, postExpression, isOffensive, isAssistance):
        self.dataHandler = dataHandler
        self.id = id
        self.preExpression = preExpression
        self.postExpression = postExpression
        self.isOffensive = isOffensive
        self.isAssistance = isAssistance