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
This file contains helper classes, which are used in attribute
calculator tests instead of Eos item classes.
"""


from eos.const import Location
from eos.fit.holder import MutableAttributeHolder


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
