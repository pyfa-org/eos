'''
Created on 11-nov.-2011

@author: cncfanatics
'''

class Module(object):
    '''
    Module class. This class is a fit-specific wrapper around a Type. It keeps track of all the fit-specific information of it.
    As this class is fit specific, the same module shouldn't be added onto more then one fit at the same time.
    '''

    def __init__(self, type):
        '''
        Constructor. Accepts a type
        '''
        self.type = type