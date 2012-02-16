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
from eos.fit.restrictionTracker.registerAbc import RestrictionRegister


class HighSlotRegister(RestrictionRegister):
    def __init__(self, fit):
        self.__fit = fit
        self.__highSlotHolders = set()

    def registerHolder(self, holder):
        if (Slot.moduleHigh in holder.item.slots) is not True:
            return
        self.__highSlotHolders.add(holder)
        self.validate()

    def unregisterHolder(self, holder):
        self.__highSlotHolders.remove(holder)

    def validate(self):
        shipHolder = self.__fit.ship
        try:
            shipHolderAttribs = shipHolder.attributes
        except AttributeError:
            highSlots = 0
        else:
            try:
                highSlots = shipHolderAttribs[Attribute.hiSlots]
            except NoAttributeException:
                highSlots = 0
        print(highSlots, len(self.__highSlotHolders))
        if len(self.__highSlotHolders) > highSlots:
            taintedHolders = set()
            taintedHolders.update(self.__highSlotHolders)
            raise HighSlotException(taintedHolders)
