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
from eos.fit.pubsub.message import InstrItemAdd, InstrItemRemove
from .base import BaseRestrictionRegister
from ..exception import RestrictionValidationError


RESTRICTION_ATTRS = (
    AttributeId.charge_group_1,
    AttributeId.charge_group_2,
    AttributeId.charge_group_3,
    AttributeId.charge_group_4,
    AttributeId.charge_group_5
)


ChargeGroupErrorData = namedtuple('ChargeGroupErrorData', ('charge_group', 'allowed_groups'))


class ChargeGroupRestrictionRegister(BaseRestrictionRegister):
    """
    Implements restriction:
    If item can fit charges and specifies group of charges it
    can fit, other groups cannot be loaded into it.

    Details:
    For validation, allowed charge group attribute values of
    eve type are taken.
    """

    def __init__(self, msg_broker):
        # Format: {container item: (allowed groups)}
        self.__restricted_containers = {}
        msg_broker._subscribe(self, self._handler_map.keys())

    def _handle_item_addition(self, message):
        # We're going to track containers, not charges;
        # ignore all items which can't fit a charge
        if not hasattr(message.item, 'charge'):
            return
        # Compose set of charge groups this container
        # is able to fit
        allowed_groups = set()
        for restriction_attr in RESTRICTION_ATTRS:
            try:
                restriction_value = message.item._eve_type.attributes[restriction_attr]
            except KeyError:
                continue
            else:
                allowed_groups.add(restriction_value)
        # Only if groups were specified, consider restriction enabled
        if allowed_groups:
            self.__restricted_containers[message.item] = tuple(allowed_groups)

    def _handle_item_removal(self, message):
        if message.item in self.__restricted_containers:
            del self.__restricted_containers[message.item]

    _handler_map = {
        InstrItemAdd: _handle_item_addition,
        InstrItemRemove: _handle_item_removal
    }

    def validate(self):
        tainted_items = {}
        # If item has charge and its group is not allowed,
        # taint charge (not container) item
        for container, allowed_groups in self.__restricted_containers.items():
            charge = container.charge
            if charge is None:
                continue
            if charge._eve_type.group not in allowed_groups:
                tainted_items[charge] = ChargeGroupErrorData(
                    charge_group=charge._eve_type.group,
                    allowed_groups=allowed_groups
                )
        if tainted_items:
            raise RestrictionValidationError(tainted_items)

    @property
    def type(self):
        return Restriction.charge_group
