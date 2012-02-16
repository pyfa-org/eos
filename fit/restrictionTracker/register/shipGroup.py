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
from eos.eve.const import Attribute
from eos.fit.attributeCalculator.exception import NoAttributeException
from eos.fit.restrictionTracker.exception import ShipGroupException
from eos.fit.restrictionTracker.registerAbc import RestrictionRegister
from eos.util.keyedSet import KeyedSet


class ShipGroupRegister(RestrictionRegister):
    def __init__(self, fit):
        self.__fit = fit
        self.__groupRestricted = KeyedSet()
        self.__restrictionAttrs = frozenset((Attribute.canFitShipGroup1, Attribute.canFitShipGroup2,
                                             Attribute.canFitShipGroup3, Attribute.canFitShipGroup4))

    def registerHolder(self, holder):
        if holder._location != Location.ship:
            return
        hasRestrictions = set()
        for restrictionAttr in self.__restrictionAttrs:
            try:
                holder.attributes[restrictionAttr]
            except NoAttributeException:
                continue
            hasRestrictions.add(restrictionAttr)
        if len(hasRestrictions) == 0:
            return
        self.__groupRestricted.addData(holder, hasRestrictions)
        self.validate()

    def unregisterHolder(self, holder):
        self.__groupRestricted.rmData(holder, self.__restrictionAttrs)

    def validate(self):
        shipHolder = self.__fit.ship
        try:
            shipGroupId = shipHolder.item.groupId
        except AttributeError:
            shipGroupId = None
        taintedHolders = set()
        for restrictedHolder in self.__groupRestricted:
            validShipGroups = set()
            for canFitShipGroupAttr in self.__groupRestricted.getData(restrictedHolder):
                validShipGroup = restrictedHolder.attributes[canFitShipGroupAttr]
                if validShipGroup is not None:
                    validShipGroups.add(validShipGroup)
            if len(validShipGroups) == 0:
                continue
            if not shipGroupId in validShipGroups:
                taintedHolders.add(restrictedHolder)
        if len(taintedHolders) > 0:
            raise ShipGroupException(taintedHolders)
