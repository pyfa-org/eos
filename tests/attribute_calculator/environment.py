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


from eos.const.eos import State, Location
from eos.fit.attribute_calculator import LinkTracker, MutableAttributeMap
from eos.tests.environment import Logger


class HolderContainer:

    def __init__(self, fit):
        self.__fit = fit
        self.__set = set()

    def add(self, holder):
        self.__set.add(holder)
        self.__fit._add_holder(holder)

    def remove(self, holder):
        self.__fit._remove_holder(holder)
        self.__set.remove(holder)

    def __len__(self):
        return len(self.__set)

    def __iter__(self):
        return iter(self.__set)


class Eos:

    def __init__(self, cache_handler):
        self._logger = Logger()
        self._cache_handler = cache_handler


class Fit:

    def __init__(self, cache_handler):
        self.eos = Eos(cache_handler)
        self._link_tracker = LinkTracker(self)
        self.__ship = None
        self.__character = None
        self.items = HolderContainer(self)

    @property
    def ship(self):
        return self.__ship

    @ship.setter
    def ship(self, ship):
        if self.__ship is not None:
            self._remove_holder(self.__ship)
        self.__ship = ship
        if ship is not None:
            self._add_holder(self.__ship)

    @property
    def character(self):
        return self.__character

    @character.setter
    def character(self, character):
        if self.__character is not None:
            self._remove_holder(self.__character)
        self.__character = character
        if character is not None:
            self._add_holder(self.__character)

    def _add_holder(self, holder):
        if holder._fit is not None:
            raise Exception
        holder._fit = self
        self._link_tracker.add_holder(holder)
        enabled_states = set(filter(lambda s: s <= holder.state, State))
        self._link_tracker.enable_states(holder, enabled_states)

    def _remove_holder(self, holder):
        if holder._fit is not self:
            raise Exception
        disabled_states = set(filter(lambda s: s <= holder.state, State))
        self._link_tracker.disable_states(holder, disabled_states)
        self._link_tracker.remove_holder(holder)
        holder._fit = None

    def _holder_state_switch(self, holder, new_state):
        enabled_states = set(filter(lambda s: holder.state < s <= new_state, State))
        disabled_states = set(filter(lambda s: new_state < s <= holder.state, State))
        self._link_tracker.enable_states(holder, enabled_states)
        self._link_tracker.disable_states(holder, disabled_states)


class Holder:

    __slots__ = ('__fit', 'item', 'attributes', '__state')

    def __init__(self, type_):
        self.__fit = None
        self.item = type_
        self.attributes = MutableAttributeMap(self)
        self.__state = State.offline

    @property
    def _fit(self):
        return self.__fit

    @_fit.setter
    def _fit(self, new_fit):
        self.attributes.clear()
        self.__fit = new_fit

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, new_state):
        old_state = self.state
        if new_state == old_state:
            return
        if self._fit is not None:
            self._fit._holder_state_switch(self, new_state)
        self.__state = new_state


class IndependentItem(Holder):

    __slots__ = ()

    def __init__(self, type_):
        Holder.__init__(self, type_)

    @property
    def _location(self):
        return None


class CharacterItem(Holder):

    __slots__ = ()

    def __init__(self, type_):
        Holder.__init__(self, type_)

    @property
    def _location(self):
        return Location.character


class ShipItem(Holder):

    __slots__ = ()

    def __init__(self, type_):
        Holder.__init__(self, type_)

    @property
    def _location(self):
        return Location.ship


class SpaceItem(Holder):

    __slots__ = ()

    def __init__(self, type_):
        Holder.__init__(self, type_)

    @property
    def _location(self):
        return Location.space


class Skill(IndependentItem):

    __slots__ = ('level',)

    def __init__(self, type_):
        IndependentItem.__init__(self, type_)
        self.level = 0


class ItemWithOther(IndependentItem):

    __slots__ = ('_other',)

    def __init__(self, type_):
        IndependentItem.__init__(self, type_)
        self._other = None

    def make_other_link(self, other):
        if self._other is not None or other._other is not None:
            raise Exception
        self._other = other
        other._other = self

    def break_other_link(self, other):
        if self._other is not other or other._other is not self:
            raise Exception
        self._other = None
        other._other = None
