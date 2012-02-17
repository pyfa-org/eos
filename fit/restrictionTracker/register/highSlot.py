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


from eos.const import Location
from eos.const import Slot
from eos.eve.const import Attribute
from eos.fit.attributeCalculator.exception import NoAttributeException
from eos.fit.restrictionTracker.exception import HighSlotException
from eos.fit.restrictionTracker.registerAbc import RestrictionRegister


class HighSlotRegister(RestrictionRegister):
    """
    Implements restriction:
    Number of high-slot holders should not exceed number of
    high slots ship provides.

    Details:
    Only holders belonging to ship are tracked.
    For validation, modified amount of high slots is taken.
    """

    def __init__(self, fit):
        self.__fit = fit
        # Container for holders which occupy
        # high slot
        # Format: {holders}
        self.__highSlotHolders = set()

    def registerHolder(self, holder):
        # Ignore holders which do not belong to ship
        if holder._location != Location.ship:
            return
        # Ignore all holders which do not occupy high slot
        if (Slot.moduleHigh in holder.item.slots) is not True:
            return
        # Just add holder to container
        self.__highSlotHolders.add(holder)

    def unregisterHolder(self, holder):
        self.__highSlotHolders.discard(holder)

    def validate(self):
        # Get number of high slots ship provides,
        # if fit doesn't have ship or ship doesn't
        # have high slot attribute, assume number
        # of provided high slots is 0
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
        # Assuming each holder takes exactly one high slot,
        # check if we have enough of them; if number of high
        # slot users is bigger than number of available high
        # slots, then all holders in container are tainted
        if len(self.__highSlotHolders) > highSlots:
            taintedHolders = set()
            taintedHolders.update(self.__highSlotHolders)
            raise HighSlotException(taintedHolders)
