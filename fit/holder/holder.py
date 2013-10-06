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


from eos.fit.attributeCalculator import MutableAttributeMap


class Holder:
    """
    Base holder class inherited by all classes that
    need to keep track of modified attributes.

    Positional arguments:
    typeId -- typeID of item, which is supposed to be
    base item for holder
    state -- state which this holder takes during initialization
    """

    __slots__ = ('_typeId', '_state', 'attributes', '__fit', 'item')

    def __init__(self, typeId, state):
        # TypeID of item this holder is supposed to wrap
        self._typeId = typeId
        # Keeps current state of the holder
        self._state = state
        # Special dictionary subclass that holds modified attributes
        # and data related to their calculation
        self.attributes = MutableAttributeMap(self)
        # Which fit this holder is bound to
        self.__fit = None
        # Which type this holder wraps
        self.item = None

    @property
    def _fit(self):
        return self.__fit

    @_fit.setter
    def _fit(self, newFit):
        self.__fit = newFit
        self._refreshContext()

    def _refreshContext(self):
        """
        Each time holder's context is changed (holder's
        fit or fit's eos), this method should be called;
        it will refresh data which is context-dependent.
        """
        self.attributes.clear()
        try:
            cacheHandler = self.__fit.eos._cacheHandler
        except AttributeError:
            self.item = None
        else:
            self.item = cacheHandler.getType(self._typeId)

    @property
    def state(self):
        return self._state

    @property
    def trackingSpeed(self):
        """Get tracking speed of holder"""
        return self.__getItemSpecificAttr('_trackingSpeedAttributeId')

    @property
    def optimalRange(self):
        """Get optimal range of holder"""
        return self.__getItemSpecificAttr('_rangeAttributeId')

    @property
    def falloffRange(self):
        """Get falloff range of holder"""
        return self.__getItemSpecificAttr('_falloffAttributeId')

    @property
    def cycleTime(self):
        return self.__getItemSpecificAttr('_durationAttributeId')

    def __getItemSpecificAttr(self, attrName):
        """Get holder attribute, which is referred by item"""
        attrId = getattr(self.item, attrName, None)
        if attrId is not None:
            try:
                attrValue = self.attributes[attrId]
            except KeyError:
                attrValue = None
        else:
            attrValue = None
        return attrValue
