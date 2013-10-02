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



class ShipResource:

    __slots__ = ('_fit', '__register', '__outputAttr')

    def __init__(self, fit, resourceUseRegister, outputAttr):
        self._fit = fit
        self.__register = resourceUseRegister
        self.__outputAttr = outputAttr

    @property
    def used(self):
        return self.__register.getResourceUse()

    @property
    def output(self):
        # Get ship's resource output, setting it to None
        # if fitting doesn't have ship assigned,
        # or ship doesn't have resource output attribute
        shipHolder = self._fit.ship
        try:
            shipHolderAttribs = shipHolder.attributes
        except AttributeError:
            return None
        else:
            try:
                return shipHolderAttribs[self.__outputAttr]
            except KeyError:
                return None
