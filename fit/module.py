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

from eos import const
from .mutableAttributeHolder import MutableAttributeHolder

class Module(MutableAttributeHolder):
    """
    Module class. This class is a fit-specific wrapper around a Type. It keeps track of all the fit-specific information of it.
    As this class is fit specific, the same module shouldn't be added onto more than one fit at the same time.
    """

    @property
    def location(self):
        return const.locShip

    def __init__(self, invType):
        """Constructor. Accepts invType"""
        super().__init__(invType)
