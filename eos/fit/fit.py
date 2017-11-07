# ==============================================================================
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
# ==============================================================================


from eos.const.eve import TypeId
from eos.data.source import Source, SourceManager
from eos.util.default import DEFAULT
from eos.util.repr import make_repr_str
from .calculator import CalculationService
from .container import (
    ItemDescriptor, ItemKeyedSet, ItemList, ItemSet, ModuleRacks)
from .helper import DamageTypes
from .item import *
from .pubsub.broker import MessageBroker
from .pubsub.message import (
    InputDefaultIncomingDamageChanged, ItemAdded, temRemoved,
    InputSourceChanged)
from .pubsub.subscriber import BaseSubscriber
from .restriction import RestrictionService
from .sim import *
from .stats import StatService
from .volatile import FitVolatileManager


class Fit(MessageBroker, BaseSubscriber):
    """Definition of fit.

    Fit is one of eos' central objects - it holds all fit items and facilities
    to calculate their attributes and do many other tasks.

    Args:
        source (optional): Source to use with this fit. When not specified,
            source which is set as default in source manager will be used.

    Attributes:
        ship: Access point for ship.
        stance: Access point for ship stance, also known as tactical mode.
        subsystems: Set for subsystems.
        modules.high: List for high-slot modules.
        modules.med: List for med-slot modules.
        modules.low: List for low-slot modules.
        rigs: Set for rigs.
        drones: Set for drones.
        fighters: Set for fighter squads.
        character: Access point for character.
        skills: Keyed set for skills.
        implants: Set for implants.
        boosters: Set for boosters.
        effect_beacon: Access point for effect beacons (e.g. wormhole effects).
        stats: All aggregated stats for fit are accessible via this access
            point.
    """

    def __init__(self, source=DEFAULT):
        MessageBroker.__init__(self)
        self.__source = None
        self.__default_incoming_damage = DamageTypes(
            em=25, thermal=25, kinetic=25, explosive=25)
        # Keep list of all items which belong to this fit
        self.__items = set()
        self._subscribe(self, self._handler_map.keys())
        # Character-related item containers
        self.skills = ItemKeyedSet(self, Skill)
        self.implants = ItemSet(self, Implant)
        self.boosters = ItemSet(self, Booster)
        # Ship-related containers
        self.subsystems = ItemSet(self, Subsystem)
        self.modules = ModuleRacks(
            high=ItemList(self, ModuleHigh),
            med=ItemList(self, ModuleMed),
            low=ItemList(self, ModuleLow))
        self.rigs = ItemSet(self, Rig)
        self.drones = ItemSet(self, Drone)
        self.fighters = ItemSet(self, FighterSquad)
        # Initialize services
        self._calculator = CalculationService(self)
        self.stats = StatService(self)
        self._restriction = RestrictionService(self, self.stats)
        self._volatile_mgr = FitVolatileManager(self, volatiles=(self.stats,))
        # Initialize simulators
        self.__rah_sim = ReactiveArmorHardenerSimulator(self)
        # Initialize source
        if source is DEFAULT:
            source = SourceManager.default
        self.source = source
        # As character object shouldn't change in any sane cases, initialize it
        # here. It has to be assigned after fit starts to track list of items
        # to make sure it's part of it
        self.character = Character(TypeId.character_static)

    ship = ItemDescriptor('_ship', Ship)
    stance = ItemDescriptor('_stance', Stance)
    character = ItemDescriptor('_character', Character)
    effect_beacon = ItemDescriptor('_effect_beacon', EffectBeacon)

    def validate(self, skip_checks=()):
        """Run fit validation.

        Args:
            skip_checks (optional): Iterable with restriction types validation
                should ignore. By default, nothing is ignored.

        Raises:
            ValidationError: If fit validation fails. Its single argument
                contains extensive data on reason of failure. Refer to
                restriction service docs for format of the data.
        """
        self._restriction.validate(skip_checks)

    @property
    def source(self):
        """Access point for fit's source.

        Source 'fills' fit with actual eve objects, which carry info about
        attributes, how they should be modified, and other important data.
        Without source set, calculating anything meaningful is not possible.
        """
        return self.__source

    @source.setter
    def source(self, new_source):
        # Attempt to fetch source from source manager if passed object is not
        # instance of source class
        if not isinstance(new_source, Source) and new_source is not None:
            new_source = SourceManager.get(new_source)
        old_source = self.source
        if new_source is old_source:
            return
        # Assign new source and send message about update
        self.__source = new_source
        self._publish(InputSourceChanged(old_source, new_source, self.__items))

    @property
    def default_incoming_damage(self):
        """Access point for default incoming damage pattern.

        This pattern will be used by default for things like EHP calculation,
        RAH adaptation, etc.
        """
        return self.__default_incoming_damage

    @default_incoming_damage.setter
    def default_incoming_damage(self, new_profile):
        old_profile = self.__default_incoming_damage
        self.__default_incoming_damage = new_profile
        if new_profile != old_profile:
            self._publish(InputDefaultIncomingDamageChanged())

    @property
    def _fit(self):
        # Items which are stored directly on the fit (e.g. ship, character)
        # refer to fit as to their container. To get fit to which item belongs,
        # container's fit is used, thus fit's fit is self
        return self

    # Message handling
    def _handle_item_addition(self, message):
        self.__items.add(message.item)

    def _handle_item_removal(self, message):
        self.__items.discard(message.item)

    _handler_map = {
        ItemAdded: _handle_item_addition,
        temRemoved: _handle_item_removal}

    # Auxiliary methods
    def __repr__(self):
        spec = [
            'ship', 'stance', 'subsystems', 'modules', 'rigs', 'drones',
            'fighters', 'character', 'skills', 'implants', 'boosters',
            'effect_beacon', 'default_incoming_damage', 'source']
        return make_repr_str(self, spec)
