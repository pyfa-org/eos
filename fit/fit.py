#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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
from .attributeCalculator import LinkTracker
from .holder.container import HolderList, HolderSet
from .holder.item import Booster, Celestial, Character, Drone, Implant, Module, Rig, Ship, Skill, Subsystem
from .restrictionTracker import RestrictionTracker
from .stats.calculator import StatsCalculator


class Fit:
    """
    Fit holds all fit items and facilities to calculate their attributes.

    Positional arguments:
    eos -- eos instance within which fit is created
    """

    def __init__(self, eos):
        # Variables used by properties
        self._ship = None
        self._character = None
        self._systemWide = None
        # Tracks links between holders assigned to fit
        self._linkTracker = LinkTracker(self)
        # Tracks various restrictions related to given fitting
        self._restrictionTracker = RestrictionTracker(self)
        # Access point for all the fitting stats
        self.stats = StatsCalculator(self)
        # Attribute metadata getter, which returns Attribute
        # objects when requesting them by ID
        self._eos = eos
        # Character-related holder containers
        self.skills = HolderSet(self, Skill)
        self.implants = HolderSet(self, Implant)
        self.boosters = HolderSet(self, Booster)
        # Ship-related containers
        self.subsystems = HolderSet(self, Subsystem)
        self.modulesHigh = HolderList(self, Module)
        self.modulesMed = HolderList(self, Module)
        self.modulesLow = HolderList(self, Module)
        self.rigs = HolderList(self, Rig)
        self.drones = HolderSet(self, Drone)

    @property
    def character(self):
        return self._character

    @character.setter
    def character(self, value):
        self._setSingleHolder('_character', Character, value)

    @property
    def ship(self):
        return self._ship

    @ship.setter
    def ship(self, value):
        self._setSingleHolder('_ship', Ship, value)

    @property
    def systemWide(self):
        return self._systemWide

    @systemWide.setter
    def systemWide(self, value):
        self._setSingleHolder('_systemWide', Celestial, value)

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
        # TODO: replace with some custom exception class
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
        # TODO: replace with some custom exception class
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

    def _setSingleHolder(self, attrName, holderClass, value):
        attrValue = getattr(self, attrName)
        if attrValue is not None:
            self._removeHolder(attrValue)
        if value is None:
            setattr(self, attrName, None)
            return
        if isinstance(value, int):
            type_ = self._eos._cacheHandler.getType(value)
            holder = holderClass(type_)
        else:
            holder = value
        setattr(self, attrName, holder)
        self._addHolder(holder)
