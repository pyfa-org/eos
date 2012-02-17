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
from eos.eve.const import Type, Attribute
from eos.fit.restrictionTracker.exception import ShipItemSizeException
from eos.fit.restrictionTracker.registerAbc import RestrictionRegister


class ShipItemSizeRegister(RestrictionRegister):
    """
    Implements restriction:
    To fit holders with volume bigger than 500, ship must
    have Capital Ships skill requirement.

    Details:
    Only holders belonging to ship are tracked.
    For validation, unmodified volume value is taken.
    """

    def __init__(self, fit):
        self.__fit = fit
        # Container for all tracked holders
        self.__shipOwnedHolders = set()

    def registerHolder(self, holder):
        # Ignore holders which do not belong to ship
        if holder._location != Location.ship:
            return
        self.__shipOwnedHolders.add(holder)

    def unregisterHolder(self, holder):
        self.__shipOwnedHolders.discard(holder)

    def validate(self):
        # Skip validation only if ship has capital
        # ships requirement, else carry on
        shipHolder = self.__fit.ship
        try:
            shipItem = shipHolder.item
        except AttributeError:
            pass
        else:
            if Type.capitalShips in shipItem.requiredSkills:
                return
        # Container for tainted holders
        taintedHolders = set()
        # Go through all ship-owned holders
        for shipOwnedHolder in self.__shipOwnedHolders:
            # Skip those which do not have volume attribute, or
            # its value is None
            holderVolume = shipOwnedHolder.item.attributes.get(Attribute.volume)
            if holderVolume is None:
                continue
            # Taint holders which are too big
            if holderVolume > 500:
                taintedHolders.add(shipOwnedHolder)
        # If there were any tainted holders, report
        # them
        if len(taintedHolders) > 0:
            raise ShipItemSizeException(taintedHolders)
