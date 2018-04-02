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


from itertools import chain

from eos.util.repr import make_repr_str


class ModuleRacks:
    """Container for all module racks.

    Each rack is actually list container for module items.
    """

    def __init__(self, high, mid, low):
        self.high = high
        self.mid = mid
        self.low = low

    def items(self):
        """Return view over all module items."""
        return ModuleItemView(self)

    def __repr__(self):
        spec = ['high', 'mid', 'low']
        return make_repr_str(self, spec)


class ModuleItemView:
    """Item view over all module items within all racks."""

    def __init__(self, racks):
        self.__racks = racks

    def __iter__(self):
        for item in chain(
            self.__racks.high,
            self.__racks.mid,
            self.__racks.low
        ):
            if item is None:
                continue
            yield item

    def __contains__(self, value):
        if value is None:
            return False
        racks = self.__racks
        return (
            racks.high.__contains__(value) or
            racks.mid.__contains__(value) or
            racks.low.__contains__(value))

    def __len__(self):
        racks_chain = chain(
            self.__racks.high, self.__racks.mid, self.__racks.low)
        return sum(item is not None for item in racks_chain)
