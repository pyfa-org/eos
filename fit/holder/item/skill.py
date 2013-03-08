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


from eos.const import Location, State
from eos.eve.const import Attribute
from eos.fit.holder import Holder


class Skill(Holder):
    """Skill with all its special properties."""

    __slots__ = ('__level',)

    def __init__(self, typeId, level=0):
        Holder.__init__(self, typeId, State.offline)
        self.__level = level

    @property
    def _location(self):
        return Location.character

    @property
    def level(self):
        return self.__level

    @level.setter
    def level(self, value):
        # Skip everything if level isn't actually
        # changed
        if self.__level == value:
            return
        self.__level = value
        # Clear everything relying on skill level,
        # if skill is assigned to fit
        if self.fit is not None:
            self.fit._linkTracker.clearHolderAttributeDependents(self, Attribute.skillLevel)
