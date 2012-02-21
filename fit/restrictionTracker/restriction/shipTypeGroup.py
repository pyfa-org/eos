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


ShipTypeGroupErrorData = namedtuple("ShipTypeGroupErrorData", ("allowedTypes", "allowedGroups", "shipType", "shipGroup"))


# Helper class-container for metadata regarding allowed
# types and groups
AllowedData = namedtuple("AllowedData", ("types", "groups"))


class ShipTypeGroupRegister(RestrictionRegister):
    """
    Implements restriction:
    Holders, which have certain fittable ship types or ship groups
    specified, can be fitted only to ships belonging to one of
    these types or groups.

    Details:
    Only holders belonging to ship are tracked.
    It's enough to satisfy any of conditions to make holder usable
    (e.g. ship's group may not satisfy canFitShipGroupX restriction,
    but its type may be suitable to use holder).
    If holder has at least one restriction attribute, it is enabled
    for tracking by this register. Please note that None-values of
    attributes enable restriction, but do not allow to fit holder to
    any ship, even if its type or group are None.
    For validation, original values of canFitShipTypeX and
    canFitShipGroupX attributes are taken.
    """

    def __init__(self, tracker):
        self._tracker = tracker
        # Container for holders which possess
        # ship type/group restriction
        # Format: {holder: allowedData}
        self.__restrictedHolders = {}

    def registerHolder(self, holder):
        # Ignore all holders which do not belong to ship
        if holder._location != Location.ship:
            return
        # Flag which is set to True if item has any of
        # the restriction attributes
        restricted = False
        # Containers for typeIDs and groupIDs of ships, to
        # which holder is allowed to fit
        allowedData = AllowedData(types=set(), groups=set())
        # Containers for attribute IDs which
        # are used to restrict fitting
        typeRestrictionAttrs = {Attribute.canFitShipType1, Attribute.canFitShipType2,
                                Attribute.canFitShipType3, Attribute.canFitShipType4,
                                Attribute.fitsToShipType}
        groupRestrictionAttrs = {Attribute.canFitShipGroup1, Attribute.canFitShipGroup2,
                                 Attribute.canFitShipGroup3, Attribute.canFitShipGroup4}
        for allowedContainer, restrictionAttrs in ((allowedData.types, typeRestrictionAttrs),
                                                   (allowedData.groups, groupRestrictionAttrs)):
            # Cycle through IDs of known restriction attributes
            for restrictionAttr in restrictionAttrs:
                # Check, if restricted attribute resides in
                # original item of our holder
                if restrictionAttr in holder.item.attributes:
                    # We set restricted flag in any case, if there's
                    # any restricted attribute, regardless of its value
                    restricted = True
                    # And add its value to corresponding set, but only
                    # if value is None
                    allowed = holder.item.attributes[restrictionAttr]
                    if allowed is not None:
                        allowedContainer.add(allowed)
        # Ignore non-restricted holders
        if restricted is not True:
            return
        # Finally, register holders which made it into here
        self.__restrictedHolders[holder] = allowedData

    def unregisterHolder(self, holder):
        if holder in self.__restrictedHolders:
            del self.__restrictedHolders[holder]

    def validate(self):
        # Get type ID and group ID of ship, if no ship
        # available, assume they're None; it's safe to set
        # them to None because our primary data container
        # with restricted holders can't contain None in its
        # values anyway
        shipHolder = self._tracker._fit.ship
        try:
            shipTypeId = shipHolder.item.id
            shipGroupId = shipHolder.item.groupId
        except AttributeError:
            shipTypeId = None
            shipGroupId = None
        # Container for tainted holders
        taintedHolders = {}
        # Go through all known restricted holders
        for holder in self.__restrictedHolders:
            allowedData = self.__restrictedHolders[holder]
            # If ship's type isn't in allowed types and ship's
            # group isn't in allowed groups, holder is tainted
            if not shipTypeId in allowedData.types and not shipGroupId in allowedData.groups:
                allowedTypes = frozenset(allowedData.types)
                allowedGroups = frozenset(allowedData.groups)
                taintedHolders[holder] = ShipTypeGroupErrorData(allowedTypes=allowedTypes,
                                                                allowedGroups=allowedGroups,
                                                                shipType=shipTypeId,
                                                                shipGroup=shipGroupId)
        # Raise error if there're any tainted holders
        if len(taintedHolders) > 0:
            raise RegisterValidationError(taintedHolders)

    @property
    def restrictionType(self):
        return Restriction.shipTypeGroup
