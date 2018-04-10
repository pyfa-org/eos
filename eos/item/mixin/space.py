# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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
# ==============================================================================


class SpaceItemMixin:
    """Defines properties of in-space items.

    Cooperative methods:
        __init__
    """

    def __init__(self, **kwargs):
        self.__coordinate = None
        self.__direction = None
        super().__init__(**kwargs)

    @property
    def coordinate(self):
        return self.__coordinate

    @coordinate.setter
    def coordinate(self, new_coordinate):
        self.__coordinate = new_coordinate

    @property
    def direction(self):
        return self.__direction

    @direction.setter
    def direction(self, new_direction):
        self.__direction = new_direction
