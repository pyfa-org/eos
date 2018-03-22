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
from eos.const.eve import AttrId
from eos.fit.message import ItemLoaded
from eos.fit.message import ItemUnloaded
from .base import BaseRestrictionRegister
from ..exception import RestrictionValidationError


ALLOWED_GROUP_ATTR_IDS = (
    AttrId.charge_group_1,
    AttrId.charge_group_2,
    AttrId.charge_group_3,
    AttrId.charge_group_4,
    AttrId.charge_group_5)


ChargeGroupErrorData = namedtuple(
    'ChargeGroupErrorData', ('group_id', 'allowed_group_ids'))


class ChargeGroupRestrictionRegister(BaseRestrictionRegister):
    """Do not allow to load charges besides those specified by container.

    Details:
        If container specifies no charge group preference, validation always
            passes.
        For validation, allowed charge group attribute values of container item
            type are taken.
    """

    def __init__(self, fit):
        # Format: {container item: (allowed groups)}
        self.__restricted_containers = {}
        fit._subscribe(self, self._handler_map.keys())

    def _handle_item_loaded(self, msg):
        # We're going to track containers, not charges; ignore all items which
        # can't fit a charge
        if not hasattr(msg.item, 'charge'):
            return
        # Compose set of charge groups this container is able to fit
        allowed_group_ids = set()
        for allowed_group_attr_id in ALLOWED_GROUP_ATTR_IDS:
            try:
                allowed_group_id = msg.item._type_attrs[allowed_group_attr_id]
            except KeyError:
                continue
            else:
                allowed_group_ids.add(allowed_group_id)
        # Only if groups were specified, consider restriction enabled
        if allowed_group_ids:
            self.__restricted_containers[msg.item] = tuple(allowed_group_ids)

    def _handle_item_unloaded(self, msg):
        if msg.item in self.__restricted_containers:
            del self.__restricted_containers[msg.item]

    _handler_map = {
        ItemLoaded: _handle_item_loaded,
        ItemUnloaded: _handle_item_unloaded}

    def validate(self):
        tainted_items = {}
        # If item has charge and its group is not allowed, taint charge item
        # (not container)
        for container, allowed_group_ids in (
            self.__restricted_containers.items()
        ):
            charge = container.charge
            if charge is None or not charge._is_loaded:
                continue
            group_id = charge._type.group_id
            if group_id not in allowed_group_ids:
                tainted_items[charge] = ChargeGroupErrorData(
                    group_id=group_id,
                    allowed_group_ids=allowed_group_ids)
        if tainted_items:
            raise RestrictionValidationError(tainted_items)

    @property
    def type(self):
        return Restriction.charge_group
