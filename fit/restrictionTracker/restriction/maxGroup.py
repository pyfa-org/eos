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


from collections import namedtuple

from eos.const import Location, Restriction
from eos.eve.const import Attribute
from eos.fit.restrictionTracker.exception import RegisterValidationError
from eos.fit.restrictionTracker.register import RestrictionRegister
from eos.util.keyedSet import KeyedSet


MaxGroupErrorData = namedtuple("MaxGroupErrorData", ("maxGroup", "holderGroup", "groupHolders"))


class MaxGroupRegister(RestrictionRegister):
    """
    Class which implements common functionality for all
    registers, which track maximum number of belonging to
    ship holders in certain state on per-group basis.
    """

    def __init__(self, maxGroupAttr, restrictionType):
        # Attribute ID whose value contains group restriction
        # of holder
        self.__maxGroupAttr = maxGroupAttr
        self.__restrictionType = restrictionType
        # Container for all tracked holders, keyed
        # by their group ID
        # Format: {group ID: {holders}}
        self.__groupAll = KeyedSet()
        # Container for holders, which have max group
        # restriction to become operational
        # Format: {holders}
        self.__maxGroupRestricted = set()

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
        self.__groupAll.addData(groupId, holder)
        # To enter restriction container, original
        # item must have restriction attribute
        if self.__maxGroupAttr in holder.item.attributes:
            self.__maxGroupRestricted.add(holder)

    def unregisterHolder(self, holder):
        # Just clear data containers
        groupId = holder.item.groupId
        self.__groupAll.rmData(groupId, holder)
        self.__maxGroupRestricted.discard(holder)

    def validate(self):
        # Container for tainted holders
        taintedHolders = {}
        # Go through all restricted holders
        for holder in self.__maxGroupRestricted:
            # Get number of registered holders, assigned to group of current
            # restricted holder, and holder's restriction value
            groupId = holder.item.groupId
            groupRegistered = len(self.__groupAll.get(groupId) or ())
            maxGroupRestriction = holder.attributes[self.__maxGroupAttr]
            # If number of registered holders from this group is bigger,
            # then current holder is tainted
            if groupRegistered > maxGroupRestriction:
                groupHolders = frozenset(self.__groupAll[groupId])
                taintedHolders[holder] = MaxGroupErrorData(maxGroup=maxGroupRestriction,
                                                           holderGroup=groupId, groupHolders=groupHolders)
        # Raise error if we detected any tainted holders
        if len(taintedHolders) > 0:
            raise RegisterValidationError(taintedHolders)

    @property
    def restrictionType(self):
        return self.__restrictionType


class MaxGroupFittedRegister(MaxGroupRegister):
    """
    Implements restriction:
    If holder has max group fitted restriction, number of fitted
    holders of this group should not exceed restriction value,
    else holder with such restriction is tainted.

    Details:
    Only holders belonging to ship are tracked.
    Only holders whose items have restriction attribute are tracked.
    For validation, modified value of restriction attribute is taken.
    """

    def __init__(self):
        MaxGroupRegister.__init__(self, Attribute.maxGroupFitted, Restriction.maxGroupFitted)


class MaxGroupOnlineRegister(MaxGroupRegister):
    """
    Implements restriction:
    If holder has max group online restriction, number of online
    holders of this group should not exceed restriction value,
    else holder with such restriction is tainted.

    Details:
    Only holders belonging to ship are tracked.
    Only holders whose items have restriction attribute are tracked.
    For validation, modified value of restriction attribute is taken.
    """

    def __init__(self):
        MaxGroupRegister.__init__(self, Attribute.maxGroupOnline, Restriction.maxGroupOnline)


class MaxGroupActiveRegister(MaxGroupRegister):
    """
    Implements restriction:
    If holder has max group active restriction, number of active
    holders of this group should not exceed restriction value,
    else holder with such restriction is tainted.

    Details:
    Only holders belonging to ship are tracked.
    Only holders whose items have restriction attribute are tracked.
    For validation, modified value of restriction attribute is taken.
    """

    def __init__(self):
        MaxGroupRegister.__init__(self, Attribute.maxGroupActive, Restriction.maxGroupActive)
