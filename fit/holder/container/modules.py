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


from itertools import chain


class ModuleRacks:
    """
    Higher-level container for all module racks
    (which are containers for holders).
    """

    __slots__ = ('high', 'med', 'low')

    def __init__(self, high, med, low):
        self.high = high
        self.med = med
        self.low = low

    def holders(self):
        """Return view over all module holders."""
        return ModuleHolderView(self)


class ModuleHolderView:
    """View over all module holders within all racks."""

    __slots__ = ('__racks',)

    def __init__(self, racks):
        self.__racks = racks

    def __iter__(self):
        racks_chain = chain(self.__racks.high, self.__racks.med, self.__racks.low)
        return (item for item in racks_chain if item is not None)

    def __contains__(self, value):
        if value is None:
            return False
        racks = self.__racks
        return (racks.high.__contains__(value) or
                racks.med.__contains__(value) or
                racks.low.__contains__(value))

    def __len__(self):
        racks_chain = chain(self.__racks.high, self.__racks.med, self.__racks.low)
        return sum(item is not None for item in racks_chain)
