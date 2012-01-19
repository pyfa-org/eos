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

from eos.calc.info.info import InfoLocation, InfoSourceType
from eos.calc.register import Register
from eos.calc.state import State


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
        self.drones = MutableAttributeHolderList(self)
        self.implants = MutableAttributeHolderList(self)
        self.boosters = MutableAttributeHolderList(self)

    @property
    def ship(self):
        """Get ship holder of fit"""
        return self.__ship

    @ship.setter
    def ship(self, ship):
        """Set ship holder of fit"""
        # Make sure to properly process ship re-set in register. Optional argument
        # is passed to make sure that all direct modifications which were applied to
        # previous ship will also apply to new one
        self._removeHolder(self.__ship, disableDirect=InfoLocation.ship)
        self.__ship = ship
        self._addHolder(self.__ship, enableDirect=InfoLocation.ship)

    @property
    def character(self):
        """Get character holder of fit"""
        return self.__character

    @character.setter
    def character(self, character):
        """Set character holder of fit"""
        # Like with ship, to re-apply effects directed to old ship, we need to pass
        # this optional argument
        self._removeHolder(self.__character, disableDirect=InfoLocation.character)
        self.__character = character
        self._addHolder(self.__character, enableDirect=InfoLocation.character)

    def _addHolder(self, holder, **kwargs):
        """Handle adding of holder to fit"""
        # Don't do anything if None was passed as holder
        if holder is None:
            return
        # Make sure the holder isn't used already
        if holder.fit is not None:
            raise ValueError("cannot add holder which is already in some fit")
        # Assign fit to holder first
        holder.fit = self
        # Only after add it to register
        self.__register.registerAffectee(holder, **kwargs)
        enabledContexts = State._contextDifference(None, holder.state)
        enabledAffectors = holder._generateAffectors(contexts=enabledContexts)
        for affector in enabledAffectors:
            self.__register.registerAffector(affector)
        # When register operations are complete, we can damage
        # all influenced by holder attributes
        self._clearAffectorDependents(enabledAffectors)
        # If holder had charge, register it too
        charge = getattr(holder, "charge", None)
        if charge is not None:
            self._addHolder(charge, enableDirect=InfoLocation.other)

    def _removeHolder(self, holder, **kwargs):
        """Handle removal of holder from fit"""
        if holder is None:
            return
        assert(holder.fit is self)
        # If there's charge in target holder, unset it first
        charge = getattr(holder, "charge", None)
        if charge is not None:
            self._removeHolder(charge, disableDirect=InfoLocation.other)
        disabledContexts = State._contextDifference(None, holder.state)
        disabledAffectors = holder._generateAffectors(contexts=disabledContexts)
        # When links in register are still alive, damage all attributes
        # influenced by holder
        self._clearAffectorDependents(disabledAffectors)
        # Remove links from register
        self.__register.unregisterAffectee(holder, **kwargs)
        for affector in disabledAffectors:
            self.__register.unregisterAffector(affector)
        # And finally, unset fit
        holder.fit = None

    def _stateSwitch(self, holder, newState):
        oldState = holder.state
        contextDiff = State._contextDifference(oldState, newState)
        affectorDiff = holder._generateAffectors(contexts=contextDiff)
        # We're turning something on
        if newState > oldState:
            for affector in affectorDiff:
                self.__register.registerAffector(affector)
            self._clearAffectorDependents(affectorDiff)
        # We're turning something off
        else:
            self._clearAffectorDependents(affectorDiff)
            for affector in affectorDiff:
                self.__register.unregisterAffector(affector)

    def _clearHolderAttributeDependents(self, holder, attrId):
        """Clear calculated attribute values relying on value of passed attribute"""
        for affector in holder._generateAffectors():
            info = affector.info
            # Skip affectors which do not use attribute being damaged as source
            if info.sourceValue != attrId or info.sourceType != InfoSourceType.attribute:
                continue
            # Gp through all holders targeted by info
            for targetHolder in self._getAffectees(affector):
                # And remove target attribute
                del targetHolder.attributes[info.targetAttribute]

    def _clearAffectorDependents(self, affectors):
        """Clear calculated attribute values relying on anything assigned to holder"""
        for affector in affectors:
            # Go through all holders targeted by info
            for targetHolder in self._getAffectees(affector):
                # And remove target attribute
                del targetHolder.attributes[affector.info.targetAttribute]

    def _getAffectors(self, holder):
        """Get set of affectors affecting passed holder"""
        return self.__register.getAffectors(holder)

    def _getAffectees(self, affector):
        """Get holders are affected by passed affector"""
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
            self.fit._removeHolder(existing)

        self.__list.__setitem__(index, holder)
        self.__fit._addHolder(holder)

    def __delitem__(self, index):
        self.__fit._removeHolder(self.__list[index])
        return self.__list.__delitem__(index)

    def __getitem__(self, index):
        return self.__list.__getitem__(index)

    def __len__(self):
        return self.__list.__len__()

    def insert(self, index, holder):
        self.__list.insert(index, holder)
        self.__fit._addHolder(holder)
