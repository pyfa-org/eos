#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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

from eos.const.eos import Restriction
from eos.const.eve import Attribute
from eos.fit.restrictionTracker.exception import RegisterValidationError
from .abc import RestrictionRegister


restrictionAttrs = (Attribute.chargeGroup1, Attribute.chargeGroup2, Attribute.chargeGroup3,
                    Attribute.chargeGroup4, Attribute.chargeGroup5)


ChargeGroupErrorData = namedtuple('ChargeGroupErrorData', ('allowedGroups', 'holderGroup'))


class ChargeGroupRegister(RestrictionRegister):
    """
    Implements restriction:
    If holder can fit charges and specifies group of charges it
    can fit, other groups cannot be loaded into it.

    Details:
    For validation, original values of allowed charge group
    attributes are taken.
    """

    def __init__(self):
        # Format: {container holder: (allowed groups)}
        self.__restrictedContainers = {}

    def registerHolder(self, holder):
        # We're going to track containers, not charges;
        # ignore all holders which can't fit a charge
        if not hasattr(holder, 'charge'):
            return
        # Compose set of charge groups this container
        # is able to fit
        allowedGroups = set()
        for restrictionAttr in restrictionAttrs:
            allowedGroups.add(holder.item.attributes.get(restrictionAttr))
        allowedGroups.discard(None)
        # Only if groups were specified, consider
        # restriction enabled
        if allowedGroups:
            self.__restrictedContainers[holder] = tuple(allowedGroups)

    def unregisterHolder(self, holder):
        if holder in self.__restrictedContainers:
            del self.__restrictedContainers[holder]

    def validate(self):
        taintedHolders = {}
        # If holder has charge and its group is not allowed,
        # taint charge (not container) holder
        for container, allowedGroups in self.__restrictedContainers.items():
            charge = container.charge
            if charge is None:
                continue
            if charge.item.groupId not in allowedGroups:
                taintedHolders[charge] = ChargeGroupErrorData(allowedGroups=allowedGroups,
                                                              holderGroup=charge.item.groupId)
        if taintedHolders:
            raise RegisterValidationError(taintedHolders)

    @property
    def restrictionType(self):
        return Restriction.chargeGroup
