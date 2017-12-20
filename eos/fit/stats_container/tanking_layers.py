# ==============================================================================
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
# ==============================================================================


from eos.util.cached_property import cached_property
from eos.util.repr import make_repr_str


class TankingLayers:
    """Container for HP stats."""

    def __init__(self, hull, armor, shield):
        self.__hull = hull
        self.__armor = armor
        self.__shield = shield

    @property
    def hull(self):
        return self.__hull

    @property
    def armor(self):
        return self.__armor

    @property
    def shield(self):
        return self.__shield

    # Iterator is needed to support tuple-style unpacking
    def __iter__(self):
        yield self.hull
        yield self.armor
        yield self.shield

    def __eq__(self, other):
        return all((
            self.hull == other.hull,
            self.armor == other.armor,
            self.shield == other.shield))

    def __hash__(self):
        return hash((
            self.__class__.__name__,
            self.hull,
            self.armor,
            self.shield))

    def __repr__(self):
        spec = ['hull', 'armor', 'shield']
        return make_repr_str(self, spec)


class TankingLayersTotal(TankingLayers):
    """Container for HP stats, which also calculates total HP."""

    @cached_property
    def total(self):
        total = (self.hull or 0) + (self.armor or 0) + (self.shield or 0)
        if (
            total == 0 and
            self.hull is None and
            self.armor is None and
            self.shield is None
        ):
            return None
        return total

    def __iter__(self):
        for item in TankingLayers.__iter__(self):
            yield item
        yield self.total

    def __repr__(self):
        spec = ['hull', 'armor', 'shield', 'total']
        return make_repr_str(self, spec)
