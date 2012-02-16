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


from eos.eve.const import Attribute
from eos.fit.attributeCalculator.exception import NoAttributeException
from eos.fit.restrictionTracker.exception import GroupFittedException
from eos.fit.restrictionTracker.registerAbc import RestrictionRegister
from eos.util.keyedSet import KeyedSet


class GroupFittedRegister(RestrictionRegister):
    def __init__(self):
        self.__groupAll = KeyedSet()
        self.__groupRestricted = set()

    def registerHolder(self, holder):
        groupId = holder.item.groupId
        if groupId is None:
            return
        self.__groupAll.addData(groupId, {holder})
        try:
            holder.attributes[Attribute.maxGroupFitted]
        except NoAttributeException:
            pass
        else:
            self.__groupRestricted.add(holder)
        self.validate()

    def unregisterHolder(self, holder):
        groupId = holder.item.groupId
        self.__groupAll.rmData(groupId, {holder})
        self.__groupRestricted.discard(holder)

    def validate(self):
        taintedHolders = set()
        for restrictedHolder in self.__groupRestricted:
            groupId = restrictedHolder.item.groupId
            groupFitted = len(self.__groupAll.getData(groupId))
            maxGroupFitted = restrictedHolder.attributes[Attribute.maxGroupFitted]
            if groupFitted > maxGroupFitted:
                taintedHolders.add(restrictedHolder)
        if len(taintedHolders) > 0:
            raise GroupFittedException(taintedHolders)
