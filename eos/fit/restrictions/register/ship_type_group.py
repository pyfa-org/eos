# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2017 Anton Vorobyov
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

from eos.const.eos import Restriction, ModifierDomain
from eos.const.eve import Attribute
from .base import BaseRestrictionRegister
from ..exception import RegisterValidationError


# Containers for attribute IDs which are used to restrict fitting
TYPE_RESTRICTION_ATTRS = (
    Attribute.can_fit_ship_type_1,
    Attribute.can_fit_ship_type_2,
    Attribute.can_fit_ship_type_3,
    Attribute.can_fit_ship_type_4,
    Attribute.can_fit_ship_type_5,
    Attribute.can_fit_ship_type_6,
    Attribute.can_fit_ship_type_7,
    Attribute.can_fit_ship_type_8,
    Attribute.can_fit_ship_type_9,
    Attribute.can_fit_ship_type_10,
    Attribute.fits_to_shiptype
)
GROUP_RESTRICTION_ATTRS = (
    Attribute.can_fit_ship_group_1,
    Attribute.can_fit_ship_group_2,
    Attribute.can_fit_ship_group_3,
    Attribute.can_fit_ship_group_4,
    Attribute.can_fit_ship_group_5,
    Attribute.can_fit_ship_group_6,
    Attribute.can_fit_ship_group_7,
    Attribute.can_fit_ship_group_8,
    Attribute.can_fit_ship_group_9,
    Attribute.can_fit_ship_group_10,
    Attribute.can_fit_ship_group_11,
    Attribute.can_fit_ship_group_12,
    Attribute.can_fit_ship_group_13,
    Attribute.can_fit_ship_group_14,
    Attribute.can_fit_ship_group_15,
    Attribute.can_fit_ship_group_16,
    Attribute.can_fit_ship_group_17,
    Attribute.can_fit_ship_group_18,
    Attribute.can_fit_ship_group_19,
    Attribute.can_fit_ship_group_20
)


ShipTypeGroupErrorData = namedtuple(
    'ShipTypeGroupErrorData',
    ('ship_type', 'ship_group', 'allowed_types', 'allowed_groups')
)


# Helper class-container for metadata regarding allowed
# types and groups
AllowedData = namedtuple('AllowedData', ('types', 'groups'))


class ShipTypeGroupRestrictionRegister(BaseRestrictionRegister):
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
    for tracking by this register.
    For validation, original values of canFitShipTypeX and
    canFitShipGroupX attributes are taken.
    """

    def __init__(self, fit):
        self._fit = fit
        # Container for holders which possess
        # ship type/group restriction
        # Format: {holder: allowedData}
        self.__restricted_holders = {}

    def register_holder(self, holder):
        # Ignore all holders which do not belong to ship
        if holder._domain != ModifierDomain.ship:
            return
        # Containers for typeIDs and groupIDs of ships, to
        # which holder is allowed to fit
        allowed_types = set()
        allowed_groups = set()
        for allowed_container, restriction_attrs in (
            (allowed_types, TYPE_RESTRICTION_ATTRS),
            (allowed_groups, GROUP_RESTRICTION_ATTRS)
        ):
            # Cycle through IDs of known restriction attributes
            for restriction_attr in restriction_attrs:
                allowed_container.add(holder.item.attributes.get(restriction_attr))
            allowed_container.discard(None)
        # Ignore non-restricted holders
        if not allowed_types and not allowed_groups:
            return
        # Finally, register holders which made it into here
        self.__restricted_holders[holder] = AllowedData(
            types=tuple(allowed_types),
            groups=tuple(allowed_groups)
        )

    def unregister_holder(self, holder):
        if holder in self.__restricted_holders:
            del self.__restricted_holders[holder]

    def validate(self):
        # Get type ID and group ID of ship, if no ship
        # available, assume they're None; it's safe to set
        # them to None because our primary data container
        # with restricted holders can't contain None in its
        # values anyway
        ship_holder = self._fit.ship
        try:
            ship_type_id = ship_holder.item.id
            ship_group = ship_holder.item.group
        except AttributeError:
            ship_type_id = None
            ship_group = None
        # Container for tainted holders
        tainted_holders = {}
        # Go through all known restricted holders
        for holder in self.__restricted_holders:
            allowed_data = self.__restricted_holders[holder]
            # If ship's type isn't in allowed types and ship's
            # group isn't in allowed groups, holder is tainted
            if ship_type_id not in allowed_data.types and ship_group not in allowed_data.groups:
                tainted_holders[holder] = ShipTypeGroupErrorData(
                    ship_type=ship_type_id,
                    ship_group=ship_group,
                    allowed_types=allowed_data.types,
                    allowed_groups=allowed_data.groups
                )
        # Raise error if there're any tainted holders
        if tainted_holders:
            raise RegisterValidationError(tainted_holders)

    @property
    def restriction_type(self):
        return Restriction.ship_type_group
