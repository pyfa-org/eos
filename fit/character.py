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

from eos.calc.mutableAttributeHolder import MutableAttributeHolder

class Character(MutableAttributeHolder):
    """
    Character class. This class represents a character.
    While it might feel counter-intuitive to track attributes on a character, some are tracked here.
    Examples: Intellect, Charisma, etc. Less obvious examples: maxGangModules, maxLockedTargets, maxActiveDrones
    Remember this class is fit-specific, don't put a single one onto two fits.
    """

    @property
    def location(self):
        return None

    def __init__(self, invType):
        """
        Constructor. Accepts a Type
        """
        super().__init__(invType)
