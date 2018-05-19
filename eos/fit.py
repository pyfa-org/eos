# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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
from eos.item import Booster
from eos.item import Character
from eos.item import Drone
from eos.item import EffectBeacon
from eos.item import FighterSquad
from eos.item import Implant
from eos.item import ModuleHigh
from eos.item import ModuleLow
from eos.item import ModuleMid
from eos.item import Rig
from eos.item import Ship
from eos.item import Skill
from eos.item import Stance
from eos.item import Subsystem
from eos.item_container import ItemDescriptor
from eos.item_container import ItemList
from eos.item_container import ItemSet
from eos.item_container import ModuleRacks
from eos.item_container import TypeUniqueItemSet
from eos.pubsub.broker import FitMsgBroker
from eos.pubsub.message import DefaultIncomingDmgChanged
from eos.pubsub.message import RahIncomingDmgChanged
from eos.restriction import RestrictionService
from eos.sim import ReactiveArmorHardenerSimulator
from eos.solar_system import SolarSystem
from eos.stats import StatService
from eos.stats_container import DmgProfile
from eos.util.default import DEFAULT
from eos.util.repr import make_repr_str


class Fit(FitMsgBroker):
    """Definition of fit.

    Fit is one of eos' central objects - it holds all fit items and facilities
    to calculate their attributes and do many other tasks.

    Args:
        solar_system (optional): Assign instantiated fit to this solar system.
            If not specified, new solar system is created.
        fleet (optional): Assign fit to fleet. If not specified, fit is not
            assigned to any fleets.

    Attributes:
        ship: Access point for ship.
        stance: Access point for ship stance, also known as tactical mode.
        subsystems: Set for subsystems.
        modules.high: List for high-slot modules.
        modules.mid: List for medium-slot modules.
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

    def __init__(self, solar_system=DEFAULT, fleet=None):
        FitMsgBroker.__init__(self)
        self.__incoming_dmg_default = None
        self.__incoming_dmg_rah = None
        # Character-related item containers
        self.skills = TypeUniqueItemSet(self, Skill)
        self.implants = ItemSet(self, Implant)
        self.boosters = ItemSet(self, Booster)
        # Ship-related containers
        self.subsystems = ItemSet(self, Subsystem)
        self.modules = ModuleRacks(
            high=ItemList(self, ModuleHigh),
            mid=ItemList(self, ModuleMid),
            low=ItemList(self, ModuleLow))
        self.rigs = ItemSet(self, Rig)
        self.drones = ItemSet(self, Drone)
        self.fighters = ItemSet(self, FighterSquad)
        # Initialize services
        self._restriction = RestrictionService(self)
        self.stats = StatService(self)
        # Initialize simulators
        self.__rah_sim = ReactiveArmorHardenerSimulator(self)
        # Initialize defaults
        self.default_incoming_dmg = DmgProfile(25, 25, 25, 25)
        # As character object shouldn't change in any sane cases, initialize it
        # here. It has to be assigned after fit starts to track list of items
        # to make sure it's part of it
        self.character = Character(TypeId.character_static)
        # Add fit to solar system
        self._solar_system = None
        if solar_system is DEFAULT:
            solar_system = SolarSystem()
        if solar_system is not None:
            solar_system.fits.add(self)
        # Add fit to fleet
        self._fleet = None
        if fleet is not None:
            fleet.fits.add(self)

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
    def solar_system(self):
        return self._solar_system

    @property
    def fleet(self):
        return self._fleet

    @property
    def default_incoming_dmg(self):
        """Access point for default incoming damage profile.

        This profile will be used by default for things like EHP calculation.
        Setter accepts only DmgProfile instances.
        """
        return self.__incoming_dmg_default

    @default_incoming_dmg.setter
    def default_incoming_dmg(self, new_profile):
        if not isinstance(new_profile, DmgProfile):
            msg = 'expected {} instance, received {} instead'.format(
                DmgProfile.__qualname__, type(new_profile).__qualname__)
            raise TypeError(msg)
        old_profile = self.__incoming_dmg_default
        self.__incoming_dmg_default = new_profile
        if new_profile != old_profile:
            self._publish(DefaultIncomingDmgChanged())
            if self.rah_incoming_dmg is None:
                self._publish(RahIncomingDmgChanged())

    @property
    def rah_incoming_dmg(self):
        """Access point for RAH incoming damage profile.

        This profile will be used for RAH adaptation. Setter accepts DmgProfile
        instances and None. When None, default incoming damage profile is used.
        """
        return self.__incoming_dmg_rah

    @rah_incoming_dmg.setter
    def rah_incoming_dmg(self, new_profile):
        if new_profile is not None and not isinstance(new_profile, DmgProfile):
            msg = 'expected {} instance or None, received {} instead'.format(
                DmgProfile.__qualname__, type(new_profile).__qualname__)
            raise TypeError(msg)
        if self.__incoming_dmg_rah is not None:
            old_profile = self.__incoming_dmg_rah
        # Use default incoming damage profile for comparison if RAH profile is
        # not set
        else:
            old_profile = self.default_incoming_dmg
        self.__incoming_dmg_rah = new_profile
        if new_profile != old_profile:
            self._publish(RahIncomingDmgChanged())

    def _unload_items(self):
        for item in self._item_iter(skip_autoitems=True):
            item._unload()

    def _load_items(self):
        for item in self._item_iter(skip_autoitems=True):
            item._load()

    # Auxiliary methods
    @property
    def _fit(self):
        # Items which are stored directly on the fit (e.g. ship, character)
        # refer to fit as to their container. To get fit to which item belongs,
        # container's fit is used, thus fit's fit is self
        return self

    def _item_iter(self, skip_autoitems=False):
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
            for child_item in item._child_item_iter(
                skip_autoitems=skip_autoitems
            ):
                yield child_item

    def _loaded_item_iter(self, skip_autoitems=False):
        for item in self._item_iter(skip_autoitems=skip_autoitems):
            if item._is_loaded:
                yield item

    def __repr__(self):
        spec = [
            'ship', 'stance', 'subsystems', 'modules', 'rigs', 'drones',
            'fighters', 'character', 'skills', 'implants', 'boosters',
            'effect_beacon', 'default_incoming_dmg']
        return make_repr_str(self, spec)
