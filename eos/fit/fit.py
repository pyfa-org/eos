# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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
# ===============================================================================


from eos.const.eos import State
from eos.const.eve import Type
from eos.data.source import SourceManager, Source
from eos.util.repr import make_repr_str
from .attribute_calculator import LinkTracker
from .exception import HolderAlreadyAssignedError, HolderFitMismatchError
from .holder.container import HolderDescriptorOnFit, HolderList, HolderRestrictedSet, HolderSet, ModuleRacks
from .restriction_tracker import RestrictionTracker
from .stat_tracker import StatTracker
from .holder.item import (
    Booster, Character, Drone, EffectBeacon, Implant, ModuleHigh,
    ModuleMed, ModuleLow, Rig, Ship, Skill, Stance, Subsystem
)


class Fit:
    """
    Fit holds all fit items and facilities to calculate their attributes.

    Optional arguments:
    source -- source to use for this fit
    """

    def __init__(self, source=None):
        self.__source = None
        # Character-related holder containers
        self.skills = HolderRestrictedSet(self, Skill)
        self.implants = HolderSet(self, Implant)
        self.boosters = HolderSet(self, Booster)
        # Ship-related containers
        self.subsystems = HolderSet(self, Subsystem)
        self.modules = ModuleRacks(
            high=HolderList(self, ModuleHigh),
            med=HolderList(self, ModuleMed),
            low=HolderList(self, ModuleLow)
        )
        self.rigs = HolderList(self, Rig)
        self.drones = HolderSet(self, Drone)
        # Service containers
        self._holders = set()
        self._volatile_holders = set()
        # Initialize services
        self._link_tracker = LinkTracker(self)  # Tracks links between holders assigned to fit
        self._restriction_tracker = RestrictionTracker(self)  # Tracks various restrictions related to given fitting
        self.stats = StatTracker(self)  # Access point for all the fitting stats
        # Use default source, unless specified otherwise
        if source is None:
            source = SourceManager.default
        self.source = source
        # As character object shouldn't change in any sane
        # cases, initialize it here
        self.character = Character(Type.character_static)

    ship = HolderDescriptorOnFit('_ship', Ship)
    stance = HolderDescriptorOnFit('_stance', Stance)
    character = HolderDescriptorOnFit('_character', Character)
    effect_beacon = HolderDescriptorOnFit('_effect_beacon', EffectBeacon)

    def validate(self, skip_checks=()):
        """
        Run fit validation.

        Optional arguments:
        skip_checks -- iterable with checks to be skipped

        Possible exceptions:
        ValidationError -- raised when validation fails
        """
        self._restriction_tracker.validate(skip_checks)

    def _request_volatile_cleanup(self, source_check=True):
        """
        Clear all the 'cached', but volatile stats, which should
        be no longer actual on any fit/holder changes. Called
        automatically be eos components when needed.

        Optional arguments:
        source_check -- check if fit has source assigned, do not
        clean if it doesn't. Default is True (do check).
        """
        if source_check is True and self.source is None:
            return
        self.stats._clear_volatile_attrs()
        for holder in self._volatile_holders:
            holder._clear_volatile_attrs()

    def _add_holder(self, holder):
        """Handle adding of holder to fit."""
        # Make sure the holder isn't used already
        if holder._fit is not None:
            raise HolderAlreadyAssignedError(holder)
        holder._fit = self
        self._holders.add(holder)
        if hasattr(holder, '_clear_volatile_attrs'):
            self._volatile_holders.add(holder)
        if self.source is not None:
            self._enable_services(holder)
        # If holder has charge, register it too
        charge = getattr(holder, 'charge', None)
        if charge is not None:
            self._add_holder(charge)

    def _remove_holder(self, holder):
        """Handle removal of holder from fit."""
        # Check that removed holder belongs to fit
        # it's removed from
        if holder._fit is not self:
            raise HolderFitMismatchError(holder)
        # If there's charge in target holder, unset it before
        # removing holder itself
        charge = getattr(holder, 'charge', None)
        if charge is not None:
            self._remove_holder(charge)
        if self.source is not None:
            self._disable_services(holder)
        self._holders.remove(holder)
        self._volatile_holders.discard(holder)
        holder._fit = None

    def _enable_services(self, holder):
        """
        Make all of the fit services aware of passed holder.
        Should be called when fit has valid source as services
        cannot work without it.
        """
        self._link_tracker.add_holder(holder)
        # Switch states upwards up to holder's state
        enabled_states = set(filter(lambda s: s <= holder.state, State))
        if len(enabled_states) > 0:
            self._link_tracker.enable_states(holder, enabled_states)
            self._restriction_tracker.enable_states(holder, enabled_states)
            self.stats._enable_states(holder, enabled_states)

    def _disable_services(self, holder):
        """Remove holder from all source-relying services."""
        # Switch states downwards from current holder's state
        disabled_states = set(filter(lambda s: s <= holder.state, State))
        if len(disabled_states) > 0:
            self.stats._disable_states(holder, disabled_states)
            self._restriction_tracker.disable_states(holder, disabled_states)
            self._link_tracker.disable_states(holder, disabled_states)
        self._link_tracker.remove_holder(holder)

    def _holder_state_switch(self, holder, new_state):
        """
        Handle fit-specific part of holder state switch.

        Required arguments:
        holder -- holder, for which state should be switched
        new_state -- state, which holder should take
        """
        # At the moment only source-dependent services are affected
        # by state switch, thus we have nothing to do if fit doesn't
        # have source assigned
        if self.source is None:
            return
        self._request_volatile_cleanup()
        # Get states which are passed during enabling/disabling
        # into single set (other should stay empty)
        enabled_states = set(filter(lambda s: holder.state < s <= new_state, State))
        disabled_states = set(filter(lambda s: new_state < s <= holder.state, State))
        # Ask trackers to perform corresponding actions
        if len(enabled_states) > 0:
            self._link_tracker.enable_states(holder, enabled_states)
            self._restriction_tracker.enable_states(holder, enabled_states)
            self.stats._enable_states(holder, enabled_states)
        elif len(disabled_states) > 0:
            self._link_tracker.disable_states(holder, disabled_states)
            self._restriction_tracker.disable_states(holder, disabled_states)
            self.stats._disable_states(holder, disabled_states)

    @property
    def source(self):
        return self.__source

    @source.setter
    def source(self, new_source):
        # Attempt to fetch source from source manager if passed object
        # is not instance of source class
        if not isinstance(new_source, Source) and new_source is not None:
            new_source = SourceManager.get(new_source)
        old_source = self.source
        # Do not update anything if sources are the same
        if new_source is old_source:
            return
        # Disable everything dependent on old source prior to switch
        if old_source is not None:
            for holder in self._holders:
                self._disable_services(holder)
        # Assign new source and feed new data to all holders
        self.__source = new_source
        self._request_volatile_cleanup(source_check=False)
        for holder in self._holders:
            holder._refresh_source()
        # Enable source-dependent services
        if new_source is not None:
            for holder in self._holders:
                self._enable_services(holder)

    def __repr__(self):
        spec = [
            'source', 'ship', 'stance', 'subsystems', 'modules', 'rigs', 'drones',
            'character', 'skills', 'implants', 'boosters'
        ]
        return make_repr_str(self, spec)
