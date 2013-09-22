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


from eos import eos as eosModule
from eos.const.eos import State
from eos.const.eve import Type
from .attributeCalculator import LinkTracker
from .exception import HolderAlreadyAssignedError, HolderFitMismatchError, HolderTypeError
from .holder import Holder
from .holder.container import HolderList, HolderSet, ModuleRacks
from .holder.item import Character
from .restrictionTracker import RestrictionTracker
from .stats.calculator import StatsCalculator


class Fit:
    """
    Fit holds all fit items and facilities to calculate their attributes.

    Keyword arguments:
    eos -- eos instance within which fit will operate. If not specified,
    eos.defaultInstance is used.
    """

    def __init__(self, eos=None):
        # Eos instance within which this fit exists; use default
        # if not specified explicitly
        if eos is None:
            self.__eos = eosModule.defaultInstance
        else:
            self.__eos = eos
        # Tracks links between holders assigned to fit
        self._linkTracker = LinkTracker(self)
        # Tracks various restrictions related to given fitting
        self._restrictionTracker = RestrictionTracker(self)
        # Access point for all the fitting stats
        self.stats = StatsCalculator(self)
        # Attributes to store holders directly assigned to fit
        self._ship = None
        self._character = None
        self._systemWide = None
        # Character-related holder containers
        self.skills = HolderSet(self)
        self.implants = HolderSet(self)
        self.boosters = HolderSet(self)
        # Ship-related containers
        self.subsystems = HolderSet(self)
        self.modules = ModuleRacks(high=HolderList(self), med=HolderList(self), low=HolderList(self))
        self.rigs = HolderList(self)
        self.drones = HolderSet(self)
        # Contains all holders currently attached to fit
        self._holders = set()
        # As character object shouldn't change in any sane
        # cases, initialize it here
        self.character = Character(Type.characterStatic)

    @property
    def eos(self):
        return self.__eos

    @eos.setter
    def eos(self, newEos):
        # Disable everything dependent on old eos prior to switch
        if self.__eos is not None:
            for holder in self._holders:
                self._holderDisableServices(holder)
        # Reassign new eos and feed new data to all holders
        self.__eos = newEos
        for holder in self._holders:
            holder._refreshContext()
        # Enable eos-dependent services for new instance
        if newEos is not None:
            for holder in self._holders:
                self._holderEnableServices(holder)

    @property
    def character(self):
        return self._character

    @character.setter
    def character(self, newCharacter):
        self.__setSingleHolder('_character', newCharacter)

    @property
    def ship(self):
        return self._ship

    @ship.setter
    def ship(self, newShip):
        self.__setSingleHolder('_ship', newShip)

    @property
    def systemWide(self):
        return self._systemWide

    @systemWide.setter
    def systemWide(self, newSystemWide):
        self.__setSingleHolder('_systemWide', newSystemWide)

    def validate(self, skipChecks=()):
        """
        Run fit validation.

        Keyword arguments:
        skipChecks -- iterable with checks to be skipped

        Possible exceptions:HolderFitMismatchError
        ValidationError -- raised when validation fails
        """
        self._restrictionTracker.validate(skipChecks)

    def _addHolder(self, holder):
        """Handle adding of holder to fit."""
        # Make sure the holder is holder and that it
        # isn't used already
        if not isinstance(holder, Holder):
            raise HolderTypeError(type(holder))
        if holder._fit is not None:
            raise HolderAlreadyAssignedError(holder)
        # Assign fit to holder first
        holder._fit = self
        self._holders.add(holder)
        if self.eos is not None:
            self._holderEnableServices(holder)
        # If holder had charge, register it too
        charge = getattr(holder, "charge", None)
        if charge is not None:
            self._addHolder(charge)

    def _removeHolder(self, holder):
        """Handle removal of holder from fit."""
        # Check that removed holder belongs to fit
        # it's removed from
        if holder._fit is not self:
            raise HolderFitMismatchError(holder)
        # If there's charge in target holder, unset it first
        charge = getattr(holder, "charge", None)
        if charge is not None:
            self._removeHolder(charge)
        if self.eos is not None:
            self._holderDisableServices(holder)
        self._holders.remove(holder)
        holder._fit = None

    def _holderEnableServices(self, holder):
        """
        Make all of the fit services aware of passed holder.
        Should be called when fit has valid Eos instance,
        as services cannot work without it.
        """
        self._linkTracker.addHolder(holder)
        # Switch states upwards up to holder's state
        enabledStates = set(filter(lambda s: s <= holder.state, State))
        if len(enabledStates) > 0:
            self._linkTracker.enableStates(holder, enabledStates)
            self._restrictionTracker.enableStates(holder, enabledStates)

    def _holderDisableServices(self, holder):
        """Remove holder from all Eos-relying services."""
        # Switch states downwards from current holder's state
        disabledStates = set(filter(lambda s: s <= holder.state, State))
        if len(disabledStates) > 0:
            self._restrictionTracker.disableStates(holder, disabledStates)
            self._linkTracker.disableStates(holder, disabledStates)
        self._linkTracker.removeHolder(holder)

    def _holderStateSwitch(self, holder, newState):
        """
        Handle fit-specific part of holder state switch.

        Positional arguments:
        holder -- holder, for which state should be switched
        newState -- state, which holder should take
        """
        # At the moment only Eos-dependent services are affected
        # by state switch, thus we have nothing to do if fit
        # doesn't have Eos assigned
        if self.eos is None:
            return
        # Get states which are passed during enabling/disabling
        # into single set (other should stay empty)
        enabledStates = set(filter(lambda s: holder.state < s <= newState, State))
        disabledStates = set(filter(lambda s: newState < s <= holder.state, State))
        # Ask trackers to perform corresponding actions
        if len(enabledStates) > 0:
            self._linkTracker.enableStates(holder, enabledStates)
            self._restrictionTracker.enableStates(holder, enabledStates)
        elif len(disabledStates) > 0:
            self._linkTracker.disableStates(holder, disabledStates)
            self._restrictionTracker.disableStates(holder, disabledStates)

    def __setSingleHolder(self, attrName, newHolder):
        """
        Handle setting of holder as fit's attribute,
        including removal of old holder assigned to it.

        Possible exceptions:
        TypeError -- raised when holder to be set is not
        None and is not Holder class/subclass instance
        ValueError -- raised when holder cannot be used
        (e.g. already belongs to some fit)
        """
        oldHolder = getattr(self, attrName)
        if oldHolder is not None:
            self._removeHolder(oldHolder)
        setattr(self, attrName, newHolder)
        if newHolder is not None:
            try:
                self._addHolder(newHolder)
            except (HolderTypeError, HolderAlreadyAssignedError) as e:
                setattr(self, attrName, oldHolder)
                if oldHolder is not None:
                    self._addHolder(oldHolder)
                exceptionMap = {HolderTypeError: TypeError,
                                HolderAlreadyAssignedError: ValueError}
                raise exceptionMap[type(e)](*e.args) from e
