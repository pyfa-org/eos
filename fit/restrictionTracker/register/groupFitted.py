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
from eos.fit.restrictionTracker.exception import GroupFittedException
from eos.fit.restrictionTracker.registerAbc import RestrictionRegister
from eos.util.keyedSet import KeyedSet


class GroupFittedRegister(RestrictionRegister):
    """
    Implements restriction:
    If holder has max group fitted restriction, number of
    holders of this group should not exceed restriction value,
    else holder with such restriction is tainted.

    Details:
    Only holders belonging to ship are tracked.
    Only holders whose items have restriction attribute are tracked.
    For validation, modified value of restriction attribute is taken.
    """

    def __init__(self):
        # Container for all fitted holders, keyed
        # by their group ID
        # Format: {group ID: {holders}}
        self.__groupAll = KeyedSet()
        # Container for holder, which have group
        # fitted restriction
        # Format: {holders}
        self.__groupRestricted = set()

    def registerHolder(self, holder):
        # Ignore holders which do not belong to ship
        if holder._location != Location.ship:
            return
        groupId = holder.item.groupId
        # Ignore holders, whose item isn't assigned
        # to any group
        if groupId is None:
            return
        # Having group ID is enough condition
        # to enter container of all fitted holders
        self.__groupAll.addData(groupId, {holder})
        # To enter restriction container, original
        # item must have restriction attribute
        if Attribute.maxGroupFitted in holder.item.attributes:
            self.__groupRestricted.add(holder)

    def unregisterHolder(self, holder):
        # Just clear data containers
        groupId = holder.item.groupId
        self.__groupAll.rmData(groupId, {holder})
        self.__groupRestricted.discard(holder)

    def validate(self):
        # Container for tainted holders
        taintedHolders = set()
        # Go through all restricted holders
        for restrictedHolder in self.__groupRestricted:
            # Get number of fitted holders, assigned to group
            # of current restricted holder, and holder's
            # restriction
            groupId = restrictedHolder.item.groupId
            groupFitted = len(self.__groupAll.getData(groupId))
            maxGroupFitted = restrictedHolder.attributes[Attribute.maxGroupFitted]
            # If number of fitted holders is bigger, then
            # current holder is tainted
            if groupFitted > maxGroupFitted:
                taintedHolders.add(restrictedHolder)
        # Raise error if we detected any tainted holders
        if len(taintedHolders) > 0:
            raise GroupFittedException(taintedHolders)
