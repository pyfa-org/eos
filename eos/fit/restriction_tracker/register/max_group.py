# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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
# ===============================================================================


from collections import namedtuple

from eos.const.eos import Domain, Restriction
from eos.const.eve import Attribute
from eos.fit.restriction_tracker.exception import RegisterValidationError
from eos.util.keyed_set import KeyedSet
from .abc import RestrictionRegister


MaxGroupErrorData = namedtuple('MaxGroupErrorData', ('holder_group', 'max_group', 'group_holders'))


class MaxGroupRegister(RestrictionRegister):
    """
    Class which implements common functionality for all
    registers, which track maximum number of belonging to
    ship holders in certain state on per-group basis.
    """

    def __init__(self, max_group_attr, restriction_type):
        # Attribute ID whose value contains group restriction
        # of holder
        self.__max_group_attr = max_group_attr
        self.__restriction_type = restriction_type
        # Container for all tracked holders, keyed
        # by their group ID
        # Format: {group ID: {holders}}
        self.__group_all = KeyedSet()
        # Container for holders, which have max group
        # restriction to become operational
        # Format: {holders}
        self.__group_restricted = set()

    def register_holder(self, holder):
        # Ignore holders which do not belong to ship
        if holder._domain != Domain.ship:
            return
        group = holder.item.group
        # Ignore holders, whose item isn't assigned
        # to any group
        if group is None:
            return
        # Having group ID is sufficient condition
        # to enter container of all fitted holders
        self.__group_all.add_data(group, holder)
        # To enter restriction container, original
        # item must have restriction attribute
        if self.__max_group_attr not in holder.item.attributes:
            return
        self.__group_restricted.add(holder)

    def unregister_holder(self, holder):
        # Just clear data containers
        group = holder.item.group
        self.__group_all.rm_data(group, holder)
        self.__group_restricted.discard(holder)

    def validate(self):
        # Container for tainted holders
        tainted_holders = {}
        # Go through all restricted holders
        for holder in self.__group_restricted:
            # Get number of registered holders, assigned to group of current
            # restricted holder, and holder's restriction value
            group = holder.item.group
            group_holders = len(self.__group_all.get(group) or ())
            max_group_restriction = holder.item.attributes[self.__max_group_attr]
            # If number of registered holders from this group is bigger,
            # then current holder is tainted
            if group_holders > max_group_restriction:
                tainted_holders[holder] = MaxGroupErrorData(
                    holder_group=group,
                    max_group=max_group_restriction,
                    group_holders=group_holders
                )
        # Raise error if we detected any tainted holders
        if tainted_holders:
            raise RegisterValidationError(tainted_holders)

    @property
    def restriction_type(self):
        return self.__restriction_type


class MaxGroupFittedRegister(MaxGroupRegister):
    """
    Implements restriction:
    If holder has max group fitted restriction, number of fitted
    holders of this group should not exceed restriction value,
    else holder with such restriction is tainted.

    Details:
    Only holders belonging to ship are tracked.
    For validation, modified value of restriction attribute is taken.
    """

    def __init__(self):
        MaxGroupRegister.__init__(self, Attribute.max_group_fitted, Restriction.max_group_fitted)


class MaxGroupOnlineRegister(MaxGroupRegister):
    """
    Implements restriction:
    If holder has max group online restriction, number of online
    holders of this group should not exceed restriction value,
    else holder with such restriction is tainted.

    Details:
    Only holders belonging to ship are tracked.
    For validation, modified value of restriction attribute is taken.
    """

    def __init__(self):
        MaxGroupRegister.__init__(self, Attribute.max_group_online, Restriction.max_group_online)


class MaxGroupActiveRegister(MaxGroupRegister):
    """
    Implements restriction:
    If holder has max group active restriction, number of active
    holders of this group should not exceed restriction value,
    else holder with such restriction is tainted.

    Details:
    Only holders belonging to ship are tracked.
    For validation, modified value of restriction attribute is taken.
    """

    def __init__(self):
        MaxGroupRegister.__init__(self, Attribute.max_group_active, Restriction.max_group_active)
