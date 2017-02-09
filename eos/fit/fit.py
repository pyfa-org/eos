# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2017 Anton Vorobyov
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
from eos.util.pubsub import MessageBroker, BaseSubscriber
from eos.util.repr import make_repr_str
from .calculator import CalculationService
from .container import ItemDescriptorOnFit, ItemList, ItemRestrictedSet, ItemSet, ModuleRacks
from .item import *
from .messages import (
    ItemAdded, ItemRemoved, EnableServices, DisableServices,
    RefreshSource, DefaultIncomingDamageChanged
)
from .restriction import RestrictionService
from .sim import *
from .stats import StatService
from .helper import DamageTypes
from .volatile import FitVolatileManager


class Fit(MessageBroker, BaseSubscriber):
    """
    Fit holds all fit items and facilities to calculate their attributes.

    Optional arguments:
    source -- source to use for this fit
    """

    def __init__(self, source=None):
        MessageBroker.__init__(self)
        self.__source = None
        self.__default_incoming_damage = DamageTypes(em=25, thermal=25, kinetic=25, explosive=25)
        # Keep list of all items which belong to this fit
        self._items = set()
        self._subscribe(self, self._handler_map.keys())
        # Character-related item containers
        self.skills = ItemRestrictedSet(self, Skill)
        self.implants = ItemSet(self, Implant)
        self.boosters = ItemSet(self, Booster)
        # Ship-related containers
        self.subsystems = ItemSet(self, Subsystem)
        self.modules = ModuleRacks(
            high=ItemList(self, ModuleHigh),
            med=ItemList(self, ModuleMed),
            low=ItemList(self, ModuleLow)
        )
        self.rigs = ItemSet(self, Rig)
        self.drones = ItemSet(self, Drone)
        # Initialize services. Some of services rely on fit structure
        # (module racks, implant set) even during initialization, thus
        # they have to be initialized after item containers
        self._calculator = CalculationService(self)
        self._restriction = RestrictionService(self)
        self.stats = StatService(self)
        self._volatile_mgr = FitVolatileManager(self, volatiles=(self.stats,))
        # Initialize simulators
        self.__rah_sim = ReactiveArmorHardenerSimulator(self)
        # Use default source, unless specified otherwise. Source setting may
        # enable services (if there's source), thus it has to be after service
        # initialization
        if source is None:
            source = SourceManager.default
        self.source = source
        # As character object shouldn't change in any sane cases, initialize it
        # here. It has to be assigned after fit starts to track list of items
        # to make sure it's part of it
        self.character = Character(Type.character_static)

    ship = ItemDescriptorOnFit('_ship', Ship)
    stance = ItemDescriptorOnFit('_stance', Stance)
    character = ItemDescriptorOnFit('_character', Character)
    effect_beacon = ItemDescriptorOnFit('_effect_beacon', EffectBeacon)

    def validate(self, skip_checks=()):
        """
        Run fit validation.

        Optional arguments:
        skip_checks -- iterable with checks to be skipped

        Possible exceptions:
        ValidationError -- raised when validation fails
        """
        self._restriction.validate(skip_checks)

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
            self._publish(DisableServices(self._items))
        # Assign new source and feed new data to all items
        self.__source = new_source
        self._publish(RefreshSource())
        # Enable source-dependent services
        if new_source is not None:
            self._publish(EnableServices(self._items))

    @property
    def default_incoming_damage(self):
        return self.__default_incoming_damage

    @default_incoming_damage.setter
    def default_incoming_damage(self, new_profile):
        old_profile = self.__default_incoming_damage
        self.__default_incoming_damage = new_profile
        if new_profile != old_profile:
            self._publish(DefaultIncomingDamageChanged())

    # Message handling
    def _handle_item_addition(self, message):
        self._items.add(message.item)

    def _handle_item_removal(self, message):
        self._items.discard(message.item)

    _handler_map = {
        ItemAdded: _handle_item_addition,
        ItemRemoved: _handle_item_removal
    }

    def _notify(self, message):
        try:
            handler = self._handler_map[type(message)]
        except KeyError:
            return
        handler(self, message)

    # Auxiliary methods
    def __repr__(self):
        spec = [
            'source', 'ship', 'stance', 'subsystems', 'modules', 'rigs', 'drones',
            'character', 'skills', 'implants', 'boosters'
        ]
        return make_repr_str(self, spec)
