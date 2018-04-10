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


from numbers import Real

from eos.util.repr import make_repr_str


class Coordinates:
    """Container for coordinate data.

    Raises:
        TypeError: If any of passed values is not a number.
    """

    def __init__(self, x, y, z):
        if not all((
            isinstance(x, Real),
            isinstance(y, Real),
            isinstance(z, Real)
        )):
            raise TypeError('all resistance values must be numbers')
        self.__x = x
        self.__y = y
        self.__z = z

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def z(self):
        return self.__z

    # Iterator is needed to support tuple-style unpacking
    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    def __eq__(self, other):
        if not isinstance(other, Coordinates):
            return NotImplemented
        return all((
            self.x == other.x,
            self.y == other.y,
            self.z == other.z))

    def __hash__(self):
        return hash((
            Coordinates.__qualname__,
            self.x,
            self.y,
            self.z))

    def __repr__(self):
        spec = ['x', 'y', 'z']
        return make_repr_str(self, spec)


class Orientation(Coordinates):
    """Container for orientation data.

    Raises:
        TypeError: If any of passed values is not a number.
        ValueError: If all passed values are zero.
    """

    def __init__(self, x, y, z):
        Coordinates.__init__(self, x, y, z)
        if all((
            x == 0,
            y == 0,
            z == 0
        )):
            raise ValueError('at least one value must be different from 0')
