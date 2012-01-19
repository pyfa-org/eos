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


from abc import ABCMeta
from abc import abstractmethod

from .affector import Affector
from .map import MutableAttributeMap
from .state import State


class MutableAttributeHolder(metaclass=ABCMeta):
    """
    Base attribute holder class inherited by all classes that need to keep track of modified attributes.
    This class holds a MutableAttributeMap to keep track of changes.
    """

    @abstractmethod
    def _getLocation(self):
        """
        Private method which each class must implement, used in
        calculation process
        """
        ...

    def __init__(self, invType):
        # Which fit this holder is bound to
        self.fit = None
        # Which invType this holder wraps
        self.invType = invType
        # Special dictionary subclass that holds modified attributes and data related to their calculation
        self.attributes = MutableAttributeMap(self)
        # Keeps current state of the holder
        self.__state = State.offline

    def _generateAffectors(self, contexts=None):
        """
        Get all affectors spawned by holder.

        Keyword arguments:
        contexts -- filter results by affector.info.requiredContext, which should be
        in this passed iterable; if None, no filtering occurs (default None)

        Return value:
        set with Affector objects
        """
        affectors = set()
        # Special handling for no filters - to avoid checking condition
        # on each cycle
        if contexts is None:
            for info in self.invType.getInfos():
                affector = Affector(self, info)
                affectors.add(affector)
        else:
            for info in self.invType.getInfos():
                if info.requiredContext in contexts:
                    affector = Affector(self, info)
                    affectors.add(affector)
        return affectors

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, newState):
        if newState > self.invType.getMaxState():
            raise RuntimeError("invalid state")
        oldState = self.state
        if newState == oldState:
            return
        if self.fit is not None:
            self.fit._stateSwitch(self, newState)
        self.__state = newState
