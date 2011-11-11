'''
Created on 11-nov.-2011

@author: cncfanatics
'''

class MyClass(object):
    '''
    Ship class. This class is fit-specific wrapper around a type, just like the Module class is.
    However, it provides helpers and calculations for when the type in question is a ship.
    As this class is fit specific, the same module shouldn't be added onto more then one fit at the same time.
    '''

    def __init__(self, type):
        '''
        Constructor. Accepts a type
        '''
        self.type = type