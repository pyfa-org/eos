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


import math

from eos.eve.const import Attribute


class StatsCalculator:
    def __init__(self, fit):
        self._fit = fit

    @property
    def agilityFactor(self):
        try:
            shipAttribs = self._fit.ship.attributes
        except AttributeError:
            return None
        try:
            agility = shipAttribs[Attribute.agility]
            mass = shipAttribs[Attribute.mass]
        except KeyError:
            return None
        realAgility = -math.log(0.25) * agility * mass / 1000000
        return realAgility

    @property
    def alignTime(self):
        try:
            return math.ceil(self.agilityFactor)
        except TypeError:
            return None
