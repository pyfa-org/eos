'''
Created on 11-nov.-2011

@author: cncfanatics
'''

class Fit(object):
    '''
    Fit object. Each fit is built out of a number of Modules, as well as a Ship.
    This class is essentialy a container, it has no logic of its own.
    '''


    def __init__(self, ship):
        '''
        Constructor: Accepts a shipType
        '''
        self.modules = []
        self.ship = ship