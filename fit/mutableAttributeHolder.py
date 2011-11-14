'''
Created on 12-nov.-2011

@author: cncfanatics
'''

import collections

class MutableAttributeHolder(object):
    '''
    Base attribute holder class inherited by all classes that need to keep track of modified attributes.
    This class holds a MutableAttributeMap to keep track of changes.
    '''


    def __init__(self, type):
        '''
        Constructor. Accepts a Type
        '''
        self.fit = None
        self.type = type
        self.attributes = MutableAttributeMap(type)

    def _apply(self):
        """
        Applies all effects of the type bound to this holder. This can have for reaching consequences as it can affect anything fitted onto the fit (including itself)
        This is typically automaticly called by eos when relevant (when a holder is added onto a fit)
        """
        fit = self.fit
        for effect in self.type.effects:
            effect._apply(fit)


    def _undo(self):
        """
        Undos the operations done by apply
        This is typically automaticly called by eos when relevant (when a holder is removed from a fit)
        """
        fit = self.fit
        for effect in self.type.effects:
            effect._undo(fit)

class MutableAttributeMap(collections.Mapping):
    '''
    MutableAttributeMap class, this class is what actualy keeps track of modified attribute values and who modified what so undo can work as expected.
    '''
    def __init__(self, type):
        self.__type = type
        self.__modifiedAttributes = {}

        # The attribute register keeps track of what effects apply to what attribute
        self.__attributeRegister = {}

    def __getitem__(self, key):
        val = self.__modifiedAttributes.get(key)
        if(val == None):
            #Should actualy run calcs here instead :D
            self.__modifiedAttributes[key] = val = self.__type.attributes[key]

        return val

    def __len__(self):
        return len(self.keys())

    def __contains__(self, key):
        return key in self.__modifiedAttributes or key in self.__type.attributes

    def __iter__(self):
        for k in self.keys():
            yield k

    def keys(self):
        return set(self.__modifiedAttributes.keys()).intersection(self.__type.attributes.keys())