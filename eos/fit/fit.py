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


from itertools import chain

from eos.const.eve import TypeId
from eos.source import Source
from eos.source import SourceManager
from eos.util.default import DEFAULT
from eos.util.pubsub.broker import MsgBroker
from eos.util.repr import make_repr_str
from .calculator import CalculationService
from .item import Booster
from .item import Character
from .item import Drone
from .item import EffectBeacon
from .item import FighterSquad
from .item import Implant
from .item import ModuleHigh
from .item import ModuleLow
from .item import ModuleMed
from .item import Rig
from .item import Ship
from .item import Skill
from .item import Stance
from .item import Subsystem
from .item_container import ItemDescriptor
from .item_container import ItemList
from .item_container import ItemSet
from .item_container import ModuleRacks
from .item_container import TypeUniqueItemSet
from .message import DefaultIncomingDmgChanged
from .message.helper import MsgHelper
from .restriction import RestrictionService
from .sim import ReactiveArmorHardenerSimulator
from .stats import StatService
from .stats_container import DmgProfile


class Fit(MsgBroker):
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
        MsgBroker.__init__(self)
        self.__source = None
        self.__default_incoming_dmg = DmgProfile(25, 25, 25, 25)
        # Character-related item containers
        self.skills = TypeUniqueItemSet(self, Skill)
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

    character = ItemDescriptor('__character', Character)
    ship = ItemDescriptor('__ship', Ship)
    stance = ItemDescriptor('__stance', Stance)
    effect_beacon = ItemDescriptor('__effect_beacon', EffectBeacon)

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
        self.__source = new_source
        # Items should be reloaded strictly one-by-one. Previously they were
        # processed in batches (send removal messages for all items, reload all
        # items, send addition messages for all items), but it caused confusion
        # in some services which could be resolved by making them more complex
        # (e.g. calculator register had to store all known affectee items
        # instead of checking if item is loaded when needed).
        for item in self._item_iter():
            # Notify everyone about item being "removed"
            msgs = MsgHelper.get_item_removed_msgs(item)
            self._publish_bulk(msgs)
            # Reload item, which clears remaining source-dependent data
            item._reload(new_source)
            # Notify everyone about item being "added"
            msgs = MsgHelper.get_item_added_msgs(item)
            self._publish_bulk(msgs)

    @property
    def default_incoming_dmg(self):
        """Access point for default incoming damage pattern.

        This pattern will be used by default for things like EHP calculation,
        RAH adaptation, etc.
        """
        return self.__default_incoming_dmg

    @default_incoming_dmg.setter
    def default_incoming_dmg(self, new_profile):
        old_profile = self.__default_incoming_dmg
        self.__default_incoming_dmg = new_profile
        if new_profile != old_profile:
            self._publish(DefaultIncomingDmgChanged())

    # Auxiliary methods
    @property
    def _fit(self):
        # Items which are stored directly on the fit (e.g. ship, character)
        # refer to fit as to their container. To get fit to which item belongs,
        # container's fit is used, thus fit's fit is self
        return self

    def _item_iter(self):
        single = (self.character, self.ship, self.stance, self.effect_beacon)
        for item in chain(
            (i for i in single if i is not None),
            self.skills,
            self.implants,
            self.boosters,
            self.subsystems,
            self.modules.items(),
            self.rigs,
            self.drones,
            self.fighters
        ):
            yield item
            for child_item in item._get_child_items():
                yield child_item

    def __repr__(self):
        spec = [
            'ship', 'stance', 'subsystems', 'modules', 'rigs', 'drones',
            'fighters', 'character', 'skills', 'implants', 'boosters',
            'effect_beacon', 'default_incoming_dmg', 'source']
        return make_repr_str(self, spec)
