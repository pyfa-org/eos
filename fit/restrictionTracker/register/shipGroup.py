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
from eos.fit.restrictionTracker.exception import ShipGroupException
from eos.fit.restrictionTracker.registerAbc import RestrictionRegister
from eos.util.keyedSet import KeyedSet


class ShipGroupRegister(RestrictionRegister):
    """
    Implements restriction:
    Holders which have certain fittable ship groups specified
    can be fitted only to ships belonging to one of these groups.

    Details:
    Only holders belonging to ship are tracked.
    For validation, unmodified values of canFitShipGroupX
    attributes is taken.
    """

    def __init__(self, fit):
        self.__fit = fit
        # Container for holders which contain
        # ship group restriction
        # Format: {holder: set(allowed ship group IDs)}
        self.__groupRestricted = KeyedSet()
        # Tuple with IDs of attributes, whose values represent
        # actual fittable groups
        self.__restrictionAttrs = (Attribute.canFitShipGroup1, Attribute.canFitShipGroup2,
                                   Attribute.canFitShipGroup3, Attribute.canFitShipGroup4)

    def registerHolder(self, holder):
        # Ignore all holders which do not belong to ship
        if holder._location != Location.ship:
            return
        # Container for attribute IDs, which restrict
        # ship group for passed holder
        allowedGroups = set()
        # Cycle through IDs of known restriction attributes
        for restrictionAttr in self.__restrictionAttrs:
            # If holder item has it and its value is not None,
            # mark its value, representing group ID, as allowed
            allowedGroup = holder.item.attributes.get(restrictionAttr)
            if allowedGroup is not None:
                allowedGroups.add(restrictionAttr)
        # Ignore holders whose items don't have any allowed
        # groups, i.e. can fit to any ship
        if len(allowedGroups) == 0:
            return
        # Finally, register holders which made it
        # into here
        self.__groupRestricted.addData(holder, allowedGroups)

    def unregisterHolder(self, holder):
        # Just discard data from container
        try:
            del self.__groupRestricted[holder]
        except KeyError:
            pass

    def validate(self):
        # Get group ID of ship, if no ship available,
        # assume it's None
        shipHolder = self.__fit.ship
        try:
            shipGroupId = shipHolder.item.groupId
        except AttributeError:
            shipGroupId = None
        # Container for tainted holders
        taintedHolders = set()
        # Go through all known restricted holders
        for restrictedHolder in self.__groupRestricted:
            allowedGroups = self.__groupRestricted.getData(restrictedHolder)
            # If ship's group isn't in allowed groups,
            # then holder is tainted
            if not shipGroupId in allowedGroups:
                taintedHolders.add(restrictedHolder)
        # Raise error if there're any tainted holders
        if len(taintedHolders) > 0:
            raise ShipGroupException(taintedHolders)
