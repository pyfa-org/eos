#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2012 Anton Vorobyov
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

from collections import MutableSequence

from .calcs import Affector
from .calcs import Register

class Fit:
    """
    Fit object. Each fit is built out of a number of Modules, as well as a Ship.
    """

    def __init__(self):
        # Variables used by properties
        self.__ship = None
        self.__character = None
        # Register-helper for partial recalculations
        self.__register = Register(self)

        # Public stuff
        self.modules = MutableAttributeHolderList(self)

    @property
    def ship(self):
        return self.__ship

    @ship.setter
    def ship(self, ship):
        if self.__ship is not None:
            self._unsetHolder(self.__ship)
        self.__ship = ship
        self._setHolder(ship)

    @property
    def character(self):
        return self.__character

    @character.setter
    def character(self, character):
        if self.__character is not None:
            self._unsetHolder(self.__character)
        self.__character = character
        self._setHolder(character)

    def _setHolder(self, holder):
        # Make sure the holder isn't used already
        if holder.fit is not None:
            raise ValueError("Cannot add a holder which is already in another fit")

        holder.fit = self
        self.__register.registerAffectee(holder)
        for affector in holder.getAffectors():
            self.__register.registerAffector(affector)
        holder._damageDependantsAll()

    def _unsetHolder(self, holder):
        assert(holder.fit == self)
        holder._damageDependantsAll()
        self.__register.unregisterAffectee(holder)
        for affector in holder.getAffectors():
            self.__register.unregisterAffector(affector)
        holder.fit = None

    def _getAffectors(self, holder):
        """Get set of affectors affecting passed holder"""
        return self.__register.getAffectors(holder)

    def _getAffectees(self, affector):
        """Get holders that the passed affector affects"""
        return self.__register.getAffectees(affector)

class MutableAttributeHolderList(MutableSequence):
    """
    Class implementing the MutableSequence ABC intended to hold a list of MutableAttributeHolders (typically: modules, drones, etc.).
    It makes sure the module knows its been added onto the fit, and makes sure a module is only in one single fit
    """
    def __init__(self, fit):
        self.__fit = fit
        self.__list = [] # List used for storage internally

    def __setitem__(self, index, holder):
        existing = self.__list.get(index)
        if(existing != None):
            self.fit._unsetHolder(existing)

        self.__list.__setitem__(index, holder)
        self.__fit._setHolder(holder)

    def __delitem__(self, index):
        self.__fit._unsetHolder(self.__list[index])
        return self.__list.__delitem__(index)

    def __getitem__(self, index):
        return self.__list.__getitem__(index)

    def __len__(self):
        return self.__list.__len__()

    def insert(self, index, holder):
        self.__list.insert(index, holder)
        self.__fit._setHolder(holder)
