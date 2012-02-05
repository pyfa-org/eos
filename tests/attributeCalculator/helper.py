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


from eos.const import Location
from eos.fit.attributeCalculator.tracker import LinkTracker
from eos.fit.holder import MutableAttributeHolder



class Fit:

    def __init__(self, attrMetaGetter):
        self._attrMetaGetter = attrMetaGetter
        self.linkTracker = LinkTracker(self)
        self.character = None
        self.ship = None

    def _addHolder(self, holder):
        holder.fit = self
        self.linkTracker._addHolder(holder)
        state = holder.state
        holder.state = None
        self.linkTracker._stateSwitch(holder, state)

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
