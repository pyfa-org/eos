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

from eos.const import State
from eos.exception import TargetException
from .map import MutableAttributeMap


class MutableAttributeHolder(metaclass=ABCMeta):
    """
    Base attribute holder class inherited by all classes that
    need to keep track of modified attributes.

    Positional arguments:
    type_ -- type (item), on which this holder is based
    """

    def __init__(self, type_):
        # Which fit this holder is bound to
        self.fit = None
        # Which type this holder wraps
        self.item = type_
        # Special dictionary subclass that holds modified attributes and data related to their calculation
        self.attributes = MutableAttributeMap(self)
        # Keeps current state of the holder
        self.__state = State.offline
        # Keeps current target of holder
        self.__target = None

    @property
    def state(self):
        """Get state of holder"""
        return self.__state

    @state.setter
    def state(self, newState):
        """Set state of holder"""
        # First, check if holder's item can have this
        # state at all
        if newState is not None and newState > self.item.maxState:
            raise RuntimeError("invalid state")
        oldState = self.state
        if newState == oldState:
            return
        # When holder is assigned to some fit, ask fit
        # to perform fit-specific state switch of our
        # holder
        if self.fit is not None:
            self.fit._linkTracker.stateSwitch(self, newState)
        self.__state = newState

    @property
    def target(self):
        """Get target, onto which holder is applied"""
        return self.__target

    @target.setter
    def target(self, newTarget):
        """Project holder onto target"""
        if self.item.isTargeted is True:
            self.__target = newTarget
        else:
            raise TargetException("attempt to project holder with non-projectable item")

    @property
    def trackingSpeed(self):
        """Get tracking speed of holder"""
        tsAttrId = self.item._trackingSpeedAttributeId
        if tsAttrId is not None:
            tracking = self.attributes[tsAttrId]
        else:
            tracking = None
        return tracking

    @property
    def optimalRange(self):
        """Get optimal range of holder"""
        orAttrId = self.item._rangeAttributeId
        if orAttrId is not None:
            optimal = self.attributes[orAttrId]
        else:
            optimal = None
        return optimal

    @property
    def falloffRange(self):
        """Get falloff range of holder"""
        frAttrId = self.item._falloffAttributeId
        if frAttrId is not None:
            falloff = self.attributes[frAttrId]
        else:
            falloff = None
        return falloff

    @property
    @abstractmethod
    def _location(self):
        """
        Service method which each class must implement, used in
        calculation process
        """
        ...
