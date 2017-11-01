# ==============================================================================
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
# ==============================================================================


from collections import namedtuple

from eos.const.eos import Restriction
from eos.const.eve import AttributeId
from eos.fit.item import ModuleHigh, ModuleLow, ModuleMed, Ship
from eos.fit.pubsub.message import InstrItemAdd, InstrItemRemove
from .base import BaseRestrictionRegister
from ..exception import RestrictionValidationError


TRACKED_ITEM_CLASSES = (ModuleHigh, ModuleMed, ModuleLow)
# Containers for attribute IDs which are used to restrict fitting
ALLOWED_TYPE_ATTR_IDS = (
    AttributeId.can_fit_ship_type_1,
    AttributeId.can_fit_ship_type_2,
    AttributeId.can_fit_ship_type_3,
    AttributeId.can_fit_ship_type_4,
    AttributeId.can_fit_ship_type_5,
    AttributeId.can_fit_ship_type_6,
    AttributeId.can_fit_ship_type_7,
    AttributeId.can_fit_ship_type_8,
    AttributeId.can_fit_ship_type_9,
    AttributeId.can_fit_ship_type_10,
    AttributeId.fits_to_shiptype)
ALLOWED_GROUP_ATTR_IDS = (
    AttributeId.can_fit_ship_group_1,
    AttributeId.can_fit_ship_group_2,
    AttributeId.can_fit_ship_group_3,
    AttributeId.can_fit_ship_group_4,
    AttributeId.can_fit_ship_group_5,
    AttributeId.can_fit_ship_group_6,
    AttributeId.can_fit_ship_group_7,
    AttributeId.can_fit_ship_group_8,
    AttributeId.can_fit_ship_group_9,
    AttributeId.can_fit_ship_group_10,
    AttributeId.can_fit_ship_group_11,
    AttributeId.can_fit_ship_group_12,
    AttributeId.can_fit_ship_group_13,
    AttributeId.can_fit_ship_group_14,
    AttributeId.can_fit_ship_group_15,
    AttributeId.can_fit_ship_group_16,
    AttributeId.can_fit_ship_group_17,
    AttributeId.can_fit_ship_group_18,
    AttributeId.can_fit_ship_group_19,
    AttributeId.can_fit_ship_group_20)


ShipTypeGroupErrorData = namedtuple(
    'ShipTypeGroupErrorData',
    ('ship_type', 'ship_group', 'allowed_types', 'allowed_groups'))


# Helper class-container for metadata regarding allowed types and groups
AllowedData = namedtuple('AllowedData', ('type_ids', 'group_ids'))


class ShipTypeGroupRestrictionRegister(BaseRestrictionRegister):
    """Make sure that item fits only to ships it can be fitted to.

    Item can specify which ships are suitable via ship group or ship type.

    Details:
        Only modules  are restricted.
        It's enough to satisfy any of conditions to make item usable (e.g.
            ship's group may not satisfy canFitShipGroupX restriction, but its
            type may be suitable to use item).
        If item has at least one restriction attribute, it is enabled for
            tracking by this register.
        For validation, canFitShipTypeX and canFitShipGroupX attribute values of
            item type are taken.
    """

    def __init__(self, msg_broker):
        self.__current_ship = None
        # Container for items which possess ship type/group restriction
        # Format: {item: allowed data}
        self.__restricted_items = {}
        msg_broker._subscribe(self, self._handler_map.keys())

    def _handle_item_addition(self, message):
        if isinstance(message.item, Ship):
            self.__current_ship = message.item
        elif not isinstance(message.item, TRACKED_ITEM_CLASSES):
            return
        # Containers for type IDs and group IDs of ships, to which item is
        # allowed to fit
        allowed_type_ids = set()
        allowed_group_ids = set()
        for allowed_container, allowed_attr_ids in (
            (allowed_type_ids, ALLOWED_TYPE_ATTR_IDS),
            (allowed_group_ids, ALLOWED_GROUP_ATTR_IDS)
        ):
            # Cycle through IDs of known restriction attributes
            for allowed_attr_id in allowed_attr_ids:
                try:
                    allowed_value = (
                        message.item._type_attributes[allowed_attr_id])
                except KeyError:
                    continue
                else:
                    allowed_container.add(allowed_value)
        # Ignore non-restricted items
        if not allowed_type_ids and not allowed_group_ids:
            return
        # Finally, register items which made it into here
        self.__restricted_items[message.item] = AllowedData(
            type_ids=tuple(allowed_type_ids),
            group_ids=tuple(allowed_group_ids))

    def _handle_item_removal(self, message):
        if message.item is self.__current_ship:
            self.__current_ship = None
        elif message.item in self.__restricted_items:
            del self.__restricted_items[message.item]

    _handler_map = {
        InstrItemAdd: _handle_item_addition,
        InstrItemRemove: _handle_item_removal}

    def validate(self):
        # Get type ID and group ID of ship, if no ship available, assume they're
        # None; it's safe to set them to None because our primary data container
        # with restricted items can't contain None in its values anyway
        try:
            ship_type_id = self.__current_ship._type_id
            ship_group_id = self.__current_ship._type.group_id
        except AttributeError:
            ship_type_id = None
            ship_group_id = None
        # Container for tainted items
        tainted_items = {}
        # Go through all known restricted items
        for item in self.__restricted_items:
            allowed_data = self.__restricted_items[item]
            # If ship's type isn't in allowed types and ship's group isn't in
            # allowed groups, item is tainted
            if (
                ship_type_id not in allowed_data.type_ids and
                ship_group_id not in allowed_data.group_ids
            ):
                tainted_items[item] = ShipTypeGroupErrorData(
                    ship_type=ship_type_id,
                    ship_group=ship_group_id,
                    allowed_types=allowed_data.type_ids,
                    allowed_groups=allowed_data.group_ids)
        # Raise error if there're any tainted items
        if tainted_items:
            raise RestrictionValidationError(tainted_items)

    @property
    def type(self):
        return Restriction.ship_type_group
