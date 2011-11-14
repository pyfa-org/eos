#===============================================================================
# Copyright (C) 2011 Diego Duclos
#
# This file is part of Eos.
#
# Eos is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Eos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Eos. If not, see <http://www.gnu.org/licenses/>.
#===============================================================================

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
        if(ship.fit != None):
            raise ValueError("Cannot add ship which is already in another fit")

        if(self.ship != None):
            self.ship._undo()

        ship.fit = self
        self.__ship = ship

        ship._apply()

    def __init__(self, ship):
        '''
        Constructor: Accepts a Ship
        '''
        self.modules = MutableAttributeHolderList(self)
        self.ship = ship

        # These registers are mainly used when new modules are added.
        # A new module addition will cause registers to be checked for all that module's skills and group for effects to apply to it
        # They usualy should NOT be changed outside the lib
        self._skillReqRegister = {}
        self._groupRegister = {}

class MutableAttributeHolderList(collections.MutableSequence):
    '''
    Class implementing the MutableSequence ABC intended to hold a list of MutableAttributeHolders (typically: modules, drones, etc.).
    It makes sure the module knows its been added onto the fit, and makes sure a module is only in one single fit
    '''
    def __init__(self, fit):
        self.__fit = fit
        self.__list = [] # List used for storage internally

    def __setitem__(self, index, holder):
        existing = self.__list.get(index)
        if(existing != None):
            self.__unsetHolder(existing)

        self.__list.__setitem__(index, holder)
        self.__setHolder(holder)

    def __delitem__(self, index):
        self.__unsetHolder(self.__list[index])
        return self.__list.__delitem__(index)

    def __getitem__(self, index):
        return self.__list.__getitem__(index)

    def __len__(self):
        return self.__list.__len__()

    def insert(self, index, holder):
        self.__list.insert(index, holder)
        self.__setHolder(holder)

    def __setHolder(self, holder):
        # Make sure the module isn't used elsewhere already
        if(holder.fit != None):
            raise ValueError("Cannot add a module which is already in another fit")

        holder.fit = self.__fit
        holder._apply()

    def __unsetHolder(self, holder):
        assert(holder.fit == self.__fit)
        holder._undo()
        holder.fit = None
