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
        self._addHolder(self.__character)

    def _addHolder(self, holder):
        """
        Handle adding of holder to fit

        Positional arguments:
        holder -- holder to be added
        """
        # Make sure the holder isn't used already
        if holder.fit is not None:
            raise RuntimeError("cannot add holder which is already in some fit")
        # Assign fit to holder first
        holder.fit = self
        # Only after add it to register
        self._linkTracker.addHolder(holder)
        self._restrictionTracker.addHolder(holder)
        self._linkTracker.stateSwitch(holder, None, holder.state)
        self._restrictionTracker.stateSwitch(holder, None, holder.state)
        # If holder had charge, register it too
        charge = getattr(holder, "charge", None)
        if charge is not None:
            self._addHolder(charge)

    def _removeHolder(self, holder):
        """
        Handle removal of holder from fit

        Positional arguments:
        holder -- holder to be removed
        """
        assert(holder.fit is self)
        # If there's charge in target holder, unset it first
        charge = getattr(holder, "charge", None)
        if charge is not None:
            self._removeHolder(charge)
        # Turn off its effects by switching state to None, then
        # unregister holder itself
        self._restrictionTracker.stateSwitch(holder, holder.state, None)
        self._linkTracker.stateSwitch(holder, holder.state, None)
        self._restrictionTracker.removeHolder(holder)
        self._linkTracker.removeHolder(holder)
        # Unset holder's fit
        holder.fit = None


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
