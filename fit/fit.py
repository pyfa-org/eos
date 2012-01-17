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

from eos.calc.info.info import InfoLocation
from eos.calc.register import Register


class Fit:
    """Fit holds all fit items and facilities to calculate their attributes"""

    def __init__(self, attrMetaGetter):
        # Variables used by properties
        self.__ship = None
        self.__character = None
        # Register-helper for partial recalculations
        self.__register = Register(self)
        # Attribute metadata getter, which returns Attribute
        # objects when requesting them by ID
        self._attrMetaGetter = attrMetaGetter
        # Item lists
        self.skills = MutableAttributeHolderList(self)
        self.modules = MutableAttributeHolderList(self)
        self.implants = MutableAttributeHolderList(self)
        self.boosters = MutableAttributeHolderList(self)

    @property
    def ship(self):
        return self.__ship

    @ship.setter
    def ship(self, ship):
        if self.__ship is not None:
            self._unsetHolder(self.__ship, disableDirect=InfoLocation.ship)
        self.__ship = ship
        self._setHolder(ship, enableDirect=InfoLocation.ship)

    @property
    def character(self):
        return self.__character

    @character.setter
    def character(self, character):
        if self.__character is not None:
            self._unsetHolder(self.__character, disableDirect=InfoLocation.character)
        self.__character = character
        self._setHolder(character, enableDirect=InfoLocation.character)

    def _setHolder(self, holder, **kwargs):
        """Handle adding of holder to fit"""
        # Make sure the holder isn't used already
        if holder.fit is not None:
            raise ValueError("cannot add holder which is already in some fit")
        # Assign fit to holder first
        holder.fit = self
        # Only after add it to register
        self.__register.registerAffectee(holder, **kwargs)
        for affector in holder.generateAffectors():
            self.__register.registerAffector(affector)
        # When register operations are complete, we can damage
        # all influenced by holder attributes
        holder._damageDependantsAll()

    def _unsetHolder(self, holder, **kwargs):
        """Handle removal of holder from fit"""
        assert(holder.fit is self)
        # If there's charge in target holder, unset it first
        charge = getattr(holder, "charge", None)
        if charge is not None:
            self._unsetHolder(charge)
        # When links in register are still alive, damage all attributes
        # influenced by holder
        holder._damageDependantsAll()
        # Remove links from register
        self.__register.unregisterAffectee(holder, **kwargs)
        for affector in holder.generateAffectors():
            self.__register.unregisterAffector(affector)
        # And finally, unset fit
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
        self.__list = []  # List used for storage internally

    def __setitem__(self, index, holder):
        existing = self.__list.get(index)
        if existing is not None:
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
