# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2017 Anton Vorobyov
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
# ===============================================================================


from numbers import Real

from eos.util.cached_property import cached_property
from eos.util.repr import make_repr_str


class DamageTypes:
    """
    Base class for all containers with damage types. Just stores
    them and provides few additional methods.
    """

    def __init__(self, em, thermal, kinetic, explosive):
        self.__em = em
        self.__thermal = thermal
        self.__kinetic = kinetic
        self.__explosive = explosive

    @property
    def em(self):
        return self.__em

    @property
    def thermal(self):
        return self.__thermal

    @property
    def kinetic(self):
        return self.__kinetic

    @property
    def explosive(self):
        return self.__explosive

    def __iter__(self):
        """Iterator is needed to support tuple-style unpacking"""
        yield self.em
        yield self.thermal
        yield self.kinetic
        yield self.explosive

    def __eq__(self, other):
        return all((
            self.em == other.em, self.thermal == other.thermal,
            self.kinetic == other.kinetic, self.explosive == other.explosive
        ))

    def __hash__(self):
        return hash((self.__class__.__name__, self.em, self.thermal, self.kinetic, self.explosive))

    def __repr__(self):
        spec = ['em', 'thermal', 'kinetic', 'explosive']
        return make_repr_str(self, spec)


class DamageTypesTotal(DamageTypes):
    """On top of storing damage type amounts, calculates their sum"""

    @cached_property
    def total(self):
        total = (self.em or 0) + (self.thermal or 0) + (self.kinetic or 0) + (self.explosive or 0)
        if total == 0 and (
            self.em is None and self.thermal is None and
            self.kinetic is None and self.explosive is None
        ):
            return None
        return total

    def __iter__(self):
        for item in DamageTypes.__iter__(self):
            yield item
        yield self.total

    def __repr__(self):
        spec = ['em', 'thermal', 'kinetic', 'explosive', 'total']
        return make_repr_str(self, spec)


class DamageProfile(DamageTypes):
    """
    Stores damage types and runs additional checks: all of damage
    values must be non-negative numbers with positive sum.
    """

    def __init__(self, em, thermal, kinetic, explosive):
        if not all((
            isinstance(em, Real), isinstance(thermal, Real),
            isinstance(kinetic, Real), isinstance(explosive, Real)
        )):
            raise TypeError('all damage types must be numbers')
        if not all((
            em >= 0, thermal >= 0, kinetic >= 0, explosive >= 0,
            em + thermal + kinetic + explosive > 0
        )):
            raise ValueError('all damage types must be non-negative numbers with positive sum')
        DamageTypes.__init__(self, em, thermal, kinetic, explosive)


class ResistanceProfile(DamageTypes):
    """
    Stores damage (or, in this case, resitance) types and runs
    additional checks: all of resistance values must be numbers
    which are not lesser than 0 and not greater than 1.
    """

    def __init__(self, em, thermal, kinetic, explosive):
        if not all((
            isinstance(em, Real), isinstance(thermal, Real),
            isinstance(kinetic, Real), isinstance(explosive, Real)
        )):
            raise TypeError('all resistances must be numbers')
        if not all((
            0 <= em <= 1, 0 <= thermal <= 1,
            0 <= kinetic <= 1, 0 <= explosive <= 1
        )):
            raise ValueError('all resistances must be within range [0, 1]')
        DamageTypes.__init__(self, em, thermal, kinetic, explosive)
