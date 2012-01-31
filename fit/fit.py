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

from eos.const import Attribute
from eos.exception import NoSlotAttributeException, SlotOccupiedException
from .aux.state import State
from .calc.info.info import InfoContext, InfoLocation, InfoSourceType
from .calc.register import Register


class Fit:
    """
    Fit holds all fit items and facilities to calculate their attributes.

    Positional arguments:
    attrMetaGetter -- getter for attribute metadata, which should return
    eve.Attribute object when ran with attribute ID passed to it
    """

    def __init__(self, attrMetaGetter):
        # Variables used by properties
        self.__ship = None
        self.__character = None
        # Register-helper for partial recalculations
        self.__register = Register(self)
        # Attribute metadata getter, which returns Attribute
        # objects when requesting them by ID
        self._attrMetaGetter = attrMetaGetter
        # Character-related holder containers
        self.skills = HolderContainer(self)
        self.implants = SlotHolderContainer(self, Attribute.implantness)
        self.boosters = SlotHolderContainer(self, Attribute.boosterness)
        # Ship-related containers
        self.subsystems = SlotHolderContainer(self, Attribute.subsystemSlot)
        self.modulesHigh = HolderContainer(self)
        self.modulesMed = HolderContainer(self)
        self.modulesLow = HolderContainer(self)
        self.drones = HolderContainer(self)
        # Celestial container
        self.systemWide = HolderContainer(self)

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
        """
        Handle adding of holder to fit

        Positional arguments:
        holder -- holder to be added

        Keyword arguments:
        Passed to one of internal registration methods
        """
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
        enabledStates = State._stateDifference(None, holder.state)
        processedContexts = {InfoContext.local}
        enabledAffectors = holder._generateAffectors(stateFilter=enabledStates, contextFilter=processedContexts)
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
        """
        Handle removal of holder from fit

        Positional arguments:
        holder -- holder to be removed

        Keyword arguments:
        Passed to one of internal unregistration methods
        """
        if holder is None:
            return
        assert(holder.fit is self)
        # If there's charge in target holder, unset it first
        charge = getattr(holder, "charge", None)
        if charge is not None:
            self._removeHolder(charge, disableDirect=InfoLocation.other)
        disabledStates = State._stateDifference(None, holder.state)
        processedContexts = {InfoContext.local}
        disabledAffectors = holder._generateAffectors(stateFilter=disabledStates, contextFilter=processedContexts)
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
        """
        Handle holder state switch in fit's context.

        Positional arguments:
        holder -- holder which has its state changed
        newState -- state which holder is taking
        """
        oldState = holder.state
        # Get set of affectors which we will need to register or
        # unregister
        stateDifference = State._stateDifference(oldState, newState)
        processedContexts = {InfoContext.local}
        affectorDiff = holder._generateAffectors(stateFilter=stateDifference, contextFilter=processedContexts)
        # Register them, if we're turning something on
        if newState > oldState:
            for affector in affectorDiff:
                self.__register.registerAffector(affector)
            self._clearAffectorDependents(affectorDiff)
        # Unregister, if we're turning something off
        else:
            self._clearAffectorDependents(affectorDiff)
            for affector in affectorDiff:
                self.__register.unregisterAffector(affector)

    def _clearHolderAttributeDependents(self, holder, attrId):
        """
        Clear calculated attributes relying on passed attribute.

        Positional arguments:
        holder -- holder, which carries attribute in question
        attrId -- ID of attribute
        """
        for affector in holder._generateAffectors():
            info = affector.info
            # Skip affectors which do not use attribute being damaged as source
            if info.sourceValue != attrId or info.sourceType != InfoSourceType.attribute:
                continue
            # Gp through all holders targeted by info
            for targetHolder in self._getAffectees(affector):
                # And remove target attribute
                del targetHolder.attributes[info.targetAttributeId]

    def _clearAffectorDependents(self, affectors):
        """
        Clear calculated attributes relying on affectors.

        Positional arguments:
        affectors -- iterable with affectors in question
        """
        for affector in affectors:
            # Go through all holders targeted by info
            for targetHolder in self._getAffectees(affector):
                # And remove target attribute
                del targetHolder.attributes[affector.info.targetAttributeId]

    def _getAffectors(self, holder):
        """
        Get affectors, influencing passed holder.

        Positional arguments:
        holder -- holder, for which we're getting affectors

        Return value:
        Set with Affector objects
        """
        return self.__register.getAffectors(holder)

    def _getAffectees(self, affector):
        """
        Get affectees being influenced by affector.

        Positional arguments:
        affector -- affector, for which we're getting affectees

        Return value:
        Set with holders
        """
        return self.__register.getAffectees(affector)


class HolderContainer:
    """
    Keep holders in plain list-like form, one instance per suitable
    for list high-level type: modules, drones, etc. It makes sure
    added/removed holders are registered/unregistered properly.

    Positional arguments:
    fit -- fit, to which list is assigned
    """
    def __init__(self, fit):
        self.__fit = fit
        self.__list = []

    def append(self, holder):
        """
        Add holder to the end of the list.

        Positional arguments:
        holder -- holder to add
        """
        self.__list.append(holder)
        self.__fit._addHolder(holder)

    def remove(self, holder):
        """
        Remove holder to from the list.

        Positional arguments:
        holder -- holder to remove

        Possible exceptions:
        ValueError -- raised when no matching holder
        is found in list
        """
        self.__list.remove(holder)
        self.__fit._removeHolder(holder)

    def insert(self, index, holder):
        """
        Insert holder to given position in list.

        Positional arguments:
        index -- position to which holder should be inserted,
        if it's out of range, holder is appended to end of list
        holder -- holder to insert
        """
        self.__list.insert(index, holder)
        self.__fit._addHolder(holder)

    def __len__(self):
        return self.__list.__len__()

    def __iter__(self):
        return (item for item in self.__list)

class SlotHolderContainer:
    """
    Keep holders in slot-based list form, one instance per suitable
    for list high-level type: implants, subsystems, etc. It makes sure
    added/removed holders are registered/unregistered properly and do not
    overlap according to slot they're taking.

    Positional arguments:
    fit -- fit, to which list is assigned
    slotAttrId -- ID of attribute which describes slot to which this item
    is fit (ID of implantness for implants, for example)
    """
    def __init__(self, fit, slotAttrId):
        self.__fit = fit
        self.__slotAttrId = slotAttrId
        self.__dict = {}

    def add(self, holder):
        """
        Add holder to dictionary.

        Positional arguments:
        holder -- holder to add

        Possible exceptions:
        eos.exceptions.NoSlotAttributeException -- raised when passed holder
        doesn't contain slot specificator
        eos.exceptions.SlotOccupiedException -- raised when slot into which
        holder should be installed is already occupied
        """
        holderItemAttrs = holder.item.attributes
        try:
            slot = holderItemAttrs[self.__slotAttrId]
        except KeyError as e:
            raise NoSlotAttributeException("item of passed holder doesn't contain slot specification") from e
        if slot in self.__dict:
            raise SlotOccupiedException("slot which passed holder is going to take is already occupied")
        self.__dict[slot] = holder
        self.__fit._addHolder(holder)

    def remove(self, holder):
        """
        Remove holder from dictionary.

        Positional arguments:
        holder -- holder to remove

        Possible exceptions:
        ValueError -- raised when passed holder can't be found in
        dictionary
        """
        holderItemAttrs = holder.item.attributes
        try:
            slot = holderItemAttrs[self.__slotAttrId]
        # Holders w/o slots can't be placed into such container,
        # thus we can be sure that there's no such holder in whole dict
        except KeyError as e:
            raise ValueError("no such holder") from e
        # If slot isn't found in dict, it means there can't be such item
        # too
        if not slot in self.__dict:
            raise ValueError("no such holder")
        # If holder occupied target slot isn't our holder, it means we
        # raise the same exception again
        if self.__dict[slot] is not holder:
            raise ValueError("no such holder")
        # Finally, remove holder
        del self.__dict[slot]
        self.__fit._removeHolder(holder)

    def __len__(self):
        return self.__dict.__len__()

    def __iter__(self):
        # Sort stuff by slot ID
        return (self.__dict[key] for key in sorted(self.__dict))
