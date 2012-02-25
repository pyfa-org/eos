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


from eos.const import State
from .attributeCalculator.tracker import LinkTracker
from .restrictionTracker.tracker import RestrictionTracker


class Fit:
    """
    Fit holds all fit items and facilities to calculate their attributes.

    Positional arguments:
    eos -- eos instance within which fit is created
    """

    def __init__(self, eos):
        # Variables used by properties
        self.__ship = None
        self.__character = None
        # Tracks links between holders assigned to fit
        self._linkTracker = LinkTracker(self)
        self._restrictionTracker = RestrictionTracker(self)
        # Attribute metadata getter, which returns Attribute
        # objects when requesting them by ID
        self._eos = eos
        # Character-related holder containers
        self.skills = HolderContainer(self)
        self.implants = HolderContainer(self)
        self.boosters = HolderContainer(self)
        # Ship-related containers
        self.subsystems = HolderContainer(self)
        self.modulesHigh = HolderContainer(self)
        self.modulesMed = HolderContainer(self)
        self.modulesLow = HolderContainer(self)
        self.rigs = HolderContainer(self)
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
        if self.__ship is not None:
            self._removeHolder(self.__ship)
        self.__ship = ship
        if ship is not None:
            self._addHolder(self.__ship)

    @property
    def character(self):
        """Get character holder of fit"""
        return self.__character

    @character.setter
    def character(self, character):
        """Set character holder of fit"""
        if self.__character is not None:
            self._removeHolder(self.__character)
        self.__character = character
        if character is not None:
            self._addHolder(self.__character)

    def validate(self, skipChecks=()):
        """
        Run fit validation.

        Keyword arguments:
        skipChecks -- iterable with checks to be skipped

        Possible exceptions:
        ValidationError -- raised when validation fails
        """
        self._restrictionTracker.validate(skipChecks=skipChecks)

    def _addHolder(self, holder):
        """
        Handle adding of holder to fit.

        Positional arguments:
        holder -- holder to be added
        """
        # Make sure the holder isn't used already
        assert(holder.fit is None)
        # Assign fit to holder first
        holder.fit = self
        # Only after add it to register
        self._linkTracker.addHolder(holder)
        # Trigger attribute links and restrictions according
        # to holder's state
        enabledStates = set(filter(lambda s: s <= holder.state, State))
        if len(enabledStates) > 0:
            self._linkTracker.enableStates(holder, enabledStates)
            self._restrictionTracker.enableStates(holder, enabledStates)
        # If holder had charge, register it too
        charge = getattr(holder, "charge", None)
        if charge is not None:
            self._addHolder(charge)

    def _removeHolder(self, holder):
        """
        Handle removal of holder from fit.

        Positional arguments:
        holder -- holder to be removed
        """
        # Check that removed holder belongs to fit
        # it's removed from
        assert(holder.fit is self)
        # If there's charge in target holder, unset it first
        charge = getattr(holder, "charge", None)
        if charge is not None:
            self._removeHolder(charge)
        # Turn off its effects by disabling all of its active states
        # and remove holder from fit altogether
        disabledStates = set(filter(lambda s: s <= holder.state, State))
        if len(disabledStates) > 0:
            self._restrictionTracker.disableStates(holder, disabledStates)
            self._linkTracker.disableStates(holder, disabledStates)
        self._linkTracker.removeHolder(holder)
        # Unset holder's fit
        holder.fit = None

    def _holderStateSwitch(self, holder, newState):
        """
        Handle fit-specific part of holder state switch.

        Positional arguments:
        holder -- holder, for which state should be switched
        newState -- state, which holder should take
        """
        # Get states which are passed during enabling/disabling
        # into single set (other should stay empty)
        enabledStates = set(filter(lambda s: s > holder.state and s <= newState, State))
        disabledStates = set(filter(lambda s: s > newState and s <= holder.state, State))
        # Only one of sets must be filled, state switch is always performed
        # either upwards or downwards, but never both
        assert(not (len(enabledStates) > 0 and len(disabledStates) > 0))
        # Ask trackers to perform corresponding actions
        if len(enabledStates) > 0:
            self._linkTracker.enableStates(holder, enabledStates)
            self._restrictionTracker.enableStates(holder, enabledStates)
        if len(disabledStates) > 0:
            self._linkTracker.disableStates(holder, disabledStates)
            self._restrictionTracker.disableStates(holder, disabledStates)


class HolderContainer:
    """
    Keep holders in plain list-like form It makes sure
    added/removed holders are registered/unregistered
    properly.

    Positional arguments:
    fit -- fit, to which list is assigned
    """
    def __init__(self, fit):
        self.__fit = fit
        self.__list = []

    # All methods which add/remove items from container
    # must perform data addition/removal to internal list
    # before/after holder fit-specific processing, as it
    # sometimes relies on presence of holder in internal
    # list (e.g. drone volume restriction register)
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
        self.__fit._removeHolder(holder)
        self.__list.remove(holder)

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
