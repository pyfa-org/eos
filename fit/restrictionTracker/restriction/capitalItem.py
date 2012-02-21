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


from eos.const import Location, Restriction
from eos.eve.const import Type, Attribute
from eos.fit.restrictionTracker.exception import RegisterValidationError
from eos.fit.restrictionTracker.register import RestrictionRegister


class CapitalItemRegister(RestrictionRegister):
    """
    Implements restriction:
    To fit holders with volume bigger than 500, ship must
    have Capital Ships skill requirement.

    Details:
    Only holders belonging to ship are tracked.
    For validation, unmodified volume value is taken.
    """

    def __init__(self, tracker):
        self._tracker = tracker
        # Container for all tracked holders
        self.__capitalHolders = set()

    def registerHolder(self, holder):
        # Ignore holders which do not belong to ship
        if holder._location != Location.ship:
            return
        # Ignore non-capital holders
        holderVolume = holder.item.attributes.get(Attribute.volume)
        if holderVolume is None or holderVolume <= 500:
            return
        self.__capitalHolders.add(holder)

    def unregisterHolder(self, holder):
        self.__capitalHolders.discard(holder)

    def validate(self):
        # Skip validation only if ship has capital
        # ships requirement, else carry on
        shipHolder = self._tracker._fit.ship
        try:
            shipItem = shipHolder.item
        except AttributeError:
            pass
        else:
            if Type.capitalShips in shipItem.requiredSkills:
                return
        # If we got here, then we're dealing with non-capital
        # ship, and all registered holders are tainted
        if len(self.__capitalHolders) > 0:
            taintedHolders = set()
            taintedHolders.update(self.__capitalHolders)
            raise RegisterValidationError(taintedHolders)

    @property
    def restrictionType(self):
        return Restriction.capitalItem
