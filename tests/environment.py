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


"""
This file contains helper classes, which implement minimalistic
version of environment in which attributeCalculator resides.
"""


from logging import getLogger

from eos.const import Location
from eos.fit.attributeCalculator.tracker import LinkTracker
from eos.fit.holder import MutableAttributeHolder


class DataHandler:
    def __init__(self, attrMetaData):
        self.__attrMetaData = attrMetaData

    def getAttribute(self, attrId):
        return self.__attrMetaData[attrId]


class Logger:
    def __init__(self):
        self.__knownSignatures = set()

    def warning(self, msg, child=None, signature=None):
        if child is None:
            logger = getLogger("eos_test")
        else:
            logger = getLogger("eos_test").getChild(child)
        if signature is None:
            logger.warning(msg)
        elif not signature in self.__knownSignatures:
            logger.warning(msg)
            self.__knownSignatures.add(signature)


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
        self._linkTracker.addHolder(holder)
        state = holder.state
        holder.state = None
        holder.fit = self
        holder.state = state

    def _removeHolder(self, holder):
        self._linkTracker.stateSwitch(holder, None)
        self._linkTracker.removeHolder(holder)
        holder.fit = None


class IndependentItem(MutableAttributeHolder):

    def __init__(self, type_):
        super().__init__(type_)

    @property
    def _location(self):
        return None


class CharacterItem(MutableAttributeHolder):

    def __init__(self, type_):
        super().__init__(type_)

    @property
    def _location(self):
        return Location.character


class ShipItem(MutableAttributeHolder):

    def __init__(self, type_):
        super().__init__(type_)

    @property
    def _location(self):
        return Location.ship


class SpaceItem(MutableAttributeHolder):

    def __init__(self, type_):
        super().__init__(type_)

    @property
    def _location(self):
        return Location.space
