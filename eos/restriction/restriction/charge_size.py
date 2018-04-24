# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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
from eos.pubsub.message import ItemLoaded
from eos.pubsub.message import ItemUnloaded
from eos.restriction.exception import RestrictionValidationError
from .base import BaseRestrictionRegister


ChargeSizeErrorData = namedtuple(
    'ChargeSizeErrorData', ('size', 'allowed_size'))


class ChargeSizeRestrictionRegister(BaseRestrictionRegister):
    """Container and charge must be of matching sizes.

    Details:
        If container doesn't specify size, charge always passes validation.
        If container specifies size and item doesn't specify it, charge is not
            allowed to be loaded.
        If container does not specify size, charge of any size can be loaded.
        To determine allowed size and charge size, item type attributes are
            used.
    """

    type = Restriction.charge_size

    def __init__(self, fit):
        self.__restricted_containers = set()
        fit._subscribe(self, self._handler_map.keys())

    def _handle_item_loaded(self, msg):
        # Ignore container items without charge attribute
        if not hasattr(msg.item, 'charge'):
            return
        # And without size specification
        if AttrId.charge_size not in msg.item._type_attrs:
            return
        self.__restricted_containers.add(msg.item)

    def _handle_item_unloaded(self, msg):
        self.__restricted_containers.discard(msg.item)

    _handler_map = {
        ItemLoaded: _handle_item_loaded,
        ItemUnloaded: _handle_item_unloaded}

    def validate(self):
        tainted_items = {}
        # Go through containers with charges, and if their sizes mismatch, taint
        # charge items
        for container in self.__restricted_containers:
            charge = container.charge
            if charge is None or not charge._is_loaded:
                continue
            container_size = container._type_attrs[AttrId.charge_size]
            charge_size = charge._type_attrs.get(AttrId.charge_size)
            if container_size != charge_size:
                tainted_items[charge] = ChargeSizeErrorData(
                    size=charge_size,
                    allowed_size=container_size)
        if tainted_items:
            raise RestrictionValidationError(tainted_items)
