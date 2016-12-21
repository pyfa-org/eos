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


from eos.const.eve import Type
from eos.data.source import SourceManager, Source
from eos.util.pubsub import MessageBroker
from eos.util.repr import make_repr_str
from .attribute_calculator import LinkTracker
from .holder.container import HolderDescriptorOnFit, HolderList, HolderRestrictedSet, HolderSet, ModuleRacks
from .holder.container.exception import HolderAlreadyAssignedError, HolderFitMismatchError
from .holder.item import *
from .restriction_tracker import RestrictionTracker
from .stat_tracker import StatTracker
from .volatile import FitVolatileManager


class Fit(MessageBroker):
    """
    Fit holds all fit items and facilities to calculate their attributes.

    Optional arguments:
    source -- source to use for this fit
    """

    def __init__(self, source=None):
        MessageBroker.__init__(self)
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
        # Initialize services
        self._link_tracker = LinkTracker(self)  # Tracks links between holders assigned to fit
        self._restriction_tracker = RestrictionTracker(self)  # Tracks various restrictions related to given fitting
        self.stats = StatTracker(self)  # Access point for all the fitting stats
        self._volatile_mgr = FitVolatileManager(self, volatiles=(self.stats,))  # Handles volatile cache cleanup
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
