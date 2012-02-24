#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2012 Anton Vorobyov
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


from eos.const import State, Location
from eos.dataHandler.exception import AttributeFetchError
from eos.fit.attributeCalculator.map import MutableAttributeMap
from eos.fit.attributeCalculator.tracker import LinkTracker
from eos.tests.environment import Logger


class DataHandler:
    def __init__(self, attrMetaData):
        self.__attrMetaData = attrMetaData

    def getAttribute(self, attrId):
        try:
            attr = self.__attrMetaData[attrId]
        except KeyError:
            raise AttributeFetchError(attrId)
        return attr


class Eos:
    def __init__(self, attrMetaData):
        self._dataHandler = DataHandler(attrMetaData)
        self._logger = Logger()


class Fit:
    def __init__(self, attrMetaData):
        self._eos = Eos(attrMetaData)
        self._linkTracker = LinkTracker(self)
        self.character = None
        self.ship = None

    def _addHolder(self, holder):
        holder.fit = self
        self._linkTracker.addHolder(holder)
        enabledStates = set(filter(lambda s: s <= holder.state, State))
        self._linkTracker.enableStates(holder, enabledStates)

    def _removeHolder(self, holder):
        disabledStates = set(filter(lambda s: s <= holder.state, State))
        self._linkTracker.disableStates(holder, disabledStates)
        self._linkTracker.removeHolder(holder)
        holder.fit = None

    def _holderStateSwitch(self, holder, newState):
        enabledStates = set(filter(lambda s: s > holder.state and s <= newState, State))
        disabledStates = set(filter(lambda s: s > newState and s <= holder.state, State))
        self._linkTracker.enableStates(holder, enabledStates)
        self._linkTracker.disableStates(holder, disabledStates)

class MutableAttributeHolder:

    __slots__ = ("__fit", "item", "attributes", "__state")

    def __init__(self, type_):
        self.__fit = None
        self.item = type_
        self.attributes = MutableAttributeMap(self)
        self.__state = State.offline

    @property
    def fit(self):
        return self.__fit

    @fit.setter
    def fit(self, newFit):
        self.attributes.clear()
        self.__fit = newFit

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, newState):
        oldState = self.state
        if newState == oldState:
            return
        if self.fit is not None:
            self.fit._holderStateSwitch(self, newState)
        self.__state = newState


class IndependentItem(MutableAttributeHolder):

    __slots__ = ()

    def __init__(self, type_):
        MutableAttributeHolder.__init__(self, type_)

    @property
    def _location(self):
        return None


class CharacterItem(MutableAttributeHolder):

    __slots__ = ()

    def __init__(self, type_):
        MutableAttributeHolder.__init__(self, type_)

    @property
    def _location(self):
        return Location.character


class ShipItem(MutableAttributeHolder):

    __slots__ = ()

    def __init__(self, type_):
        MutableAttributeHolder.__init__(self, type_)

    @property
    def _location(self):
        return Location.ship


class SpaceItem(MutableAttributeHolder):

    __slots__ = ()

    def __init__(self, type_):
        MutableAttributeHolder.__init__(self, type_)

    @property
    def _location(self):
        return Location.space


class Skill(IndependentItem):
    __slots__ = ("level",)

    def __init__(self, type_):
        CharacterItem.__init__(self, type_)
        self.level = 0


class ItemWithOther(IndependentItem):
    __slots__ = ("_other",)

    def __init__(self, type_):
        CharacterItem.__init__(self, type_)
        self._other = None
