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
from eos.fit.attributeCalculator.exception import NoAttributeException
from eos.fit.restrictionTracker.exception import ShipItemSizeException
from eos.fit.restrictionTracker.registerAbc import RestrictionRegister


class ShipItemSizeRegister(RestrictionRegister):
    def __init__(self, fit):
        self.__fit = fit
        self.__shipOwnedHolders = set()

    def registerHolder(self, holder):
        if holder._location != Location.ship:
            return
        self.__shipOwnedHolders.add(holder)
        self.validate()

    def unregisterHolder(self, holder):
        self.__shipOwnedHolders.remove(holder)

    def validate(self):
        shipHolder = self.__fit.ship
        try:
            shipItem = shipHolder.item
        except AttributeError:
            pass
        else:
            if Type.capitalShips in shipItem.requiredSkills:
                return
        taintedHolders = set()
        for shipOwnedHolder in self.__shipOwnedHolders:
            try:
                holderVolume = shipOwnedHolder.attributes[Attribute.volume]
            except NoAttributeException:
                continue
            if holderVolume > 500:
                taintedHolders.add(shipOwnedHolder)
        if len(taintedHolders) > 0:
            raise ShipItemSizeException(taintedHolders)
