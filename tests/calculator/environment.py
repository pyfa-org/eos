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


from unittest.mock import Mock

from eos.const.eos import State, ModifierDomain
from eos.fit.calculator import CalculationService, MutableAttributeMap
from eos.fit.messages import HolderAdded, HolderRemoved, HolderStateChanged, EnableServices


class HolderContainer:

    def __init__(self, fit):
        self.__fit = fit
        self.__set = set()

    def add(self, holder):
        self.__set.add(holder)
        holder._fit = self.__fit
        self.__fit._calculator._notify(HolderAdded(holder))

    def remove(self, holder):
        self.__fit._calculator._notify(HolderRemoved(holder))
        holder._fit = None
        self.__set.remove(holder)

    def __len__(self):
        return len(self.__set)


class Source:

    def __init__(self, cache_handler):
        self.cache_handler = cache_handler


class Fit:

    def __init__(self, cache_handler, msgstore_filter=None):
        self.source = Source(cache_handler)
        self._calculator = CalculationService(self)
        self._calculator._notify(EnableServices(holders=()))
        self.__ship = None
        self.__character = None
        self.items = HolderContainer(self)
        self.__msgstore_filter = msgstore_filter
        self.message_store = []

    @property
    def ship(self):
        return self.__ship

    @ship.setter
    def ship(self, new_ship):
        old_ship = self.__ship
        if old_ship is not None:
            self._calculator._notify(HolderRemoved(old_ship))
            old_ship._fit = None
        self.__ship = new_ship
        if new_ship is not None:
            new_ship._fit = self
            self._calculator._notify(HolderAdded(new_ship))

    @property
    def character(self):
        return self.__character

    @character.setter
    def character(self, new_char):
        old_char = self.__character
        if old_char is not None:
            self._calculator._notify(HolderRemoved(old_char))
            old_char._fit = None
        self.__character = new_char
        if new_char is not None:
            new_char._fit = self
            self._calculator._notify(HolderAdded(new_char))

    def _publish(self, message):
        if self.__msgstore_filter is None or self.__msgstore_filter(message) is True:
            self.message_store.append(message)
        self._calculator._notify(message)

    _subscribe = Mock()


class Holder:

    def __init__(self, type_):
        self.__fit = None
        self._type_id = type_.id
        self.item = type_
        self.attributes = MutableAttributeMap(self)
        self._disabled_effects = set()
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
        old_state = self.__state
        self.__state = new_state
        if self.__fit is not None:
            self.__fit._calculator._notify(HolderStateChanged(self, old_state, new_state))

    @property
    def _enabled_effects(self):
        return set(e.id for e in self.item.effects).difference(self._disabled_effects)


class IndependentItem(Holder):

    def __init__(self, type_):
        Holder.__init__(self, type_)

    @property
    def _domain(self):
        return None

    @property
    def _owner_modifiable(self):
        return False


class CharacterItem(Holder):

    def __init__(self, type_):
        Holder.__init__(self, type_)

    @property
    def _domain(self):
        return ModifierDomain.character

    @property
    def _owner_modifiable(self):
        return False


class ShipItem(Holder):

    def __init__(self, type_):
        Holder.__init__(self, type_)

    @property
    def _domain(self):
        return ModifierDomain.ship

    @property
    def _owner_modifiable(self):
        return False


class OwnModItem(Holder):

    def __init__(self, type_):
        Holder.__init__(self, type_)

    @property
    def _domain(self):
        return None

    @property
    def _owner_modifiable(self):
        return True


class ContainerHolder(IndependentItem):

    def __init__(self, type_):
        IndependentItem.__init__(self, type_)
        self.charge = None


class ChargeHolder(IndependentItem):

    def __init__(self, type_):
        IndependentItem.__init__(self, type_)
        self.container = None
