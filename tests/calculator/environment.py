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


from eos.const.eos import State, ModifierDomain
from eos.fit.calculator import CalculationService, MutableAttributeMap
from eos.fit.messages import ItemAdded, ItemRemoved, ItemStateChanged, EnableServices
from eos.util.pubsub import MessageBroker


class ItemContainer:

    def __init__(self, fit):
        self.__fit = fit
        self.__set = set()

    def add(self, item):
        self.__set.add(item)
        item._fit = self.__fit
        self.__fit._calculator._notify(ItemAdded(item))

    def remove(self, item):
        self.__fit._calculator._notify(ItemRemoved(item))
        item._fit = None
        self.__set.remove(item)

    def __len__(self):
        return len(self.__set)


class Source:

    def __init__(self, cache_handler):
        self.cache_handler = cache_handler


class Fit(MessageBroker):

    def __init__(self, cache_handler, msgstore_filter=None):
        MessageBroker.__init__(self)
        self.source = Source(cache_handler)
        self.__msgstore_filter = msgstore_filter
        self.message_store = []
        self._calculator = CalculationService(self)
        self._calculator._notify(EnableServices(items=()))
        # Containers
        self.__ship = None
        self.__character = None
        self.items = ItemContainer(self)

    @property
    def ship(self):
        return self.__ship

    @ship.setter
    def ship(self, new_ship):
        old_ship = self.__ship
        if old_ship is not None:
            self._calculator._notify(ItemRemoved(old_ship))
            old_ship._fit = None
        self.__ship = new_ship
        if new_ship is not None:
            new_ship._fit = self
            self._calculator._notify(ItemAdded(new_ship))

    @property
    def character(self):
        return self.__character

    @character.setter
    def character(self, new_char):
        old_char = self.__character
        if old_char is not None:
            self._calculator._notify(ItemRemoved(old_char))
            old_char._fit = None
        self.__character = new_char
        if new_char is not None:
            new_char._fit = self
            self._calculator._notify(ItemAdded(new_char))

    def _publish(self, message):
        if self.__msgstore_filter is None or self.__msgstore_filter(message) is True:
            self.message_store.append(message)
        MessageBroker._publish(self, message)


class BaseItem:

    def __init__(self, eve_type):
        self.__fit = None
        self._eve_type_id = eve_type.id
        self._eve_type = eve_type
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
            self.__fit._calculator._notify(ItemStateChanged(self, old_state, new_state))

    @property
    def _enabled_effects(self):
        return set(e.id for e in self._eve_type.effects).difference(self._disabled_effects)


class IndependentItem(BaseItem):

    _parent_modifier_domain = None
    _owner_modifiable = False


class CharDomainItem(BaseItem):

    _parent_modifier_domain = ModifierDomain.character
    _owner_modifiable = False


class ShipDomainItem(BaseItem):

    _parent_modifier_domain = ModifierDomain.ship
    _owner_modifiable = False


class OwnerModifiableItem(BaseItem):

    _parent_modifier_domain = None
    _owner_modifiable = True


class ContainerItem(IndependentItem):

    def __init__(self, eve_type):
        IndependentItem.__init__(self, eve_type)
        self.charge = None


class ChargeItem(IndependentItem):

    def __init__(self, eve_type):
        IndependentItem.__init__(self, eve_type)
        self.container = None
