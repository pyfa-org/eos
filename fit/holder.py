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


from eos.const import State
from .attributeCalculator.map import MutableAttributeMap


class MutableAttributeHolder:
    """
    Base attribute holder class inherited by all classes that
    need to keep track of modified attributes.

    Positional arguments:
    type_ -- type (item), on which this holder is based
    """

    __slots__ = ("__fit", "item", "attributes", "__state", "__target")

    def __init__(self, type_):
        # Which fit this holder is bound to
        self.__fit = None
        # Which type this holder wraps
        self.item = type_
        # Special dictionary subclass that holds modified attributes and data related to their calculation
        self.attributes = MutableAttributeMap(self)
        # Keeps current state of the holder
        self.__state = State.offline
        # Keeps current target of holder
        self.__target = None

    @property
    def fit(self):
        """Get fit to which holder is assigned"""
        return self.__fit

    @fit.setter
    def fit(self, newFit):
        """Assign holder to fit"""
        # Our modified attributes have some value only within
        # fit context; when fit changes, they must be cleaned
        self.attributes.clear()
        self.__fit = newFit

    @property
    def state(self):
        """Get state of holder"""
        return self.__state

    @state.setter
    def state(self, newState):
        """Set state of holder"""
        # First, check if holder's item can have this
        # state at all
        # TODO: probably move this check to restriction tracker,
        # or throw custom exception
        validStates = filter(lambda state: state <= self.item.maxState, State)
        if not newState in validStates:
            raise RuntimeError("invalid state")
        if newState == self.state:
            return
        # When holder is assigned to some fit, ask fit to perform
        # fit-specific state switch of our holder
        if self.fit is not None:
            self.fit._holderStateSwitch(self, newState)
        self.__state = newState

#    @property
#    def target(self):
#        """Get target, onto which holder is applied"""
#        return self.__target
#
#    @target.setter
#    def target(self, newTarget):
#        """Project holder onto target"""
#        if self.item.isTargeted is True:
#            self.__target = newTarget
#        else:
#            raise TargetException("attempt to project holder with non-projectable item")

    @property
    def trackingSpeed(self):
        """Get tracking speed of holder"""
        tsAttrId = self.item._trackingSpeedAttributeId
        if tsAttrId is not None:
            try:
                tracking = self.attributes[tsAttrId]
            except KeyError:
                tracking = None
        else:
            tracking = None
        return tracking

    @property
    def optimalRange(self):
        """Get optimal range of holder"""
        orAttrId = self.item._rangeAttributeId
        if orAttrId is not None:
            try:
                optimal = self.attributes[orAttrId]
            except KeyError:
                optimal = None
        else:
            optimal = None
        return optimal

    @property
    def falloffRange(self):
        """Get falloff range of holder"""
        frAttrId = self.item._falloffAttributeId
        if frAttrId is not None:
            try:
                falloff = self.attributes[frAttrId]
            except KeyError:
                falloff = None
        else:
            falloff = None
        return falloff

    @property
    def cycleTime(self):
        """Get cycle time of holder"""
        ctAttrId = self.item._durationAttributeId
        if ctAttrId is not None:
            try:
                cycleTime = self.attributes[ctAttrId]
            except KeyError:
                cycleTime = None
        else:
            cycleTime = None
        return cycleTime
