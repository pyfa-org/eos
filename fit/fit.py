'''
Created on 11-nov.-2011

@author: cncfanatics

This file is part of eos.

eos is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Eos is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with eos.  If not, see <http://www.gnu.org/licenses/>.
'''

import collections

class Fit(object):
    '''
    Fit object. Each fit is built out of a number of Modules, as well as a Ship.
    This class is essentialy a container, it has minimal logic.
    '''

    @property
    def ship(self):
        return self.__ship

    @ship.setter
    def ship(self, ship):
        assert(ship.fit == None)
        ship.fit = self
        self.__ship = ship

    def __init__(self, ship):
        '''
        Constructor: Accepts a Ship
        '''
        self.modules = ModuleList(self)
        self.ship = ship

class ModuleList():
    '''
    Class implementing the MutableSequence ABC intended to hold a list of modules.
    It makes sure the module knows its been added onto the fit, and makes sure a module is only in one single fit
    '''
    __metaclass__ = collections.MutableSequence

    def __init__(self, fit):
        self.__fit = fit
        self.__list = [] # List used for storage internally

    def __setitem__(self, index, module):
        self.__setModule(module)
        return self.__list.__setitem__(index, module)

    def __delitem__(self, index):
        module = self.__list.get(index)
        assert(module.fit == self.__fit) #Make sure stuff matches
        module.fit = None #Set the fit of the to be removed module to None
        return self.__list.__delitem__(index)

    def insert(self, index, module):
        self.__setModule(module)
        return self.__list.insert(index, module)

    def __setModule(self, module):
        assert(module.fit == None) # Make sure the module isn't used elsewhere already
        module.fit = self.__fit