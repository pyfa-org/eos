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


from collections import namedtuple

from eos.const.eos import State, Domain
from eos.fit.attribute_calculator import LinkTracker, MutableAttributeMap


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


class Source:

    def __init__(self, cache_handler):
        self.cache_handler = cache_handler


class Fit:

    def __init__(self, cache_handler):
        self.source = Source(cache_handler)
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

    def __init__(self, type_):
        Holder.__init__(self, type_)

    @property
    def _domain(self):
        return None


class CharacterItem(Holder):

    def __init__(self, type_):
        Holder.__init__(self, type_)

    @property
    def _domain(self):
        return Domain.character


class ShipItem(Holder):

    def __init__(self, type_):
        Holder.__init__(self, type_)

    @property
    def _domain(self):
        return Domain.ship


class SpaceItem(Holder):

    def __init__(self, type_):
        Holder.__init__(self, type_)

    @property
    def _domain(self):
        return Domain.space


class Skill(IndependentItem):

    def __init__(self, type_):
        IndependentItem.__init__(self, type_)
        self.level = 0


class ContainerHolder(IndependentItem):

    def __init__(self, type_):
        IndependentItem.__init__(self, type_)
        self.charge = None


class ChargeHolder(IndependentItem):

    def __init__(self, type_):
        IndependentItem.__init__(self, type_)
        self.container = None
