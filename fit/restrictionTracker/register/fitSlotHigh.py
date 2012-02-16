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


from eos.const import Slot
from eos.eve.const import Attribute
from eos.fit.attributeCalculator.exception import NoAttributeException
from eos.fit.restrictionTracker.exception import HighSlotException

class FitSlotHighRegister:
    def __init__(self, fit):
        self.__fit = fit
        self.__resUsers = set()

    def registerHolder(self, holder):
        resUse = Slot.moduleHigh in holder.item.slots
        if resUse is not True:
            return
        resUsed = len(self.__resUsers)
        try:
            resMax = self.__fit.ship.attributes[Attribute.hiSlots]
        except NoAttributeException:
            resMax = 0
        if resUsed + 1 > resMax:
            raise HighSlotException
        self.__resUsers.add(holder)

    def unregisterHolder(self, holder):
        self.__resUsers.remove(holder)
