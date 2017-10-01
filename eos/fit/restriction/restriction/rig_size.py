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
from eos.const.eve import AttributeId, EffectId
from eos.fit.item import Ship
from eos.fit.pubsub.message import InstrEffectsStart, InstrEffectsStop, InstrItemAdd, InstrItemRemove
from .base import BaseRestrictionRegister
from ..exception import RestrictionValidationError


RigSizeErrorData = namedtuple('RigSizeErrorData', ('item_size', 'allowed_size'))


class RigSizeRestrictionRegister(BaseRestrictionRegister):
    """
    Implements restriction:
    If ship requires rigs of certain size, rigs of other size cannot
    be used.

    Details:
    For validation, rig_size attribute value of eve type is taken.
    """

    def __init__(self, msg_broker):
        self.__current_ship = None
        # Container for items which have rig size restriction
        self.__restricted_items = set()
        msg_broker._subscribe(self, self._handler_map.keys())

    def _handle_item_addition(self, message):
        if isinstance(message.item, Ship):
            self.__current_ship = message.item

    def _handle_item_removal(self, message):
        if message.item is self.__current_ship:
            self.__current_ship = None

    def _handle_item_effects_activation(self, message):
        if EffectId.rig_slot in message.effects and AttributeId.rig_size in message.item._eve_type.attributes:
            self.__restricted_items.add(message.item)

    def _handle_item_effects_deactivation(self, message):
        if EffectId.rig_slot in message.effects:
            self.__restricted_items.discard(message.item)

    _handler_map = {
        InstrItemAdd: _handle_item_addition,
        InstrItemRemove: _handle_item_removal,
        InstrEffectsStart: _handle_item_effects_activation,
        InstrEffectsStop: _handle_item_effects_deactivation
    }

    def validate(self):
        # Do not apply restriction when fit doesn't have ship
        try:
            ship_eve_type = self.__current_ship._eve_type
        except AttributeError:
            return
        # If ship doesn't have restriction attribute,
        # allow all rigs - skip validation
        try:
            allowed_rig_size = ship_eve_type.attributes[AttributeId.rig_size]
        except KeyError:
            return
        tainted_items = {}
        for item in self.__restricted_items:
            item_rig_size = item._eve_type.attributes[AttributeId.rig_size]
            # If rig size specification on item and ship differs,
            # then item is tainted
            if item_rig_size != allowed_rig_size:
                tainted_items[item] = RigSizeErrorData(
                    item_size=item_rig_size,
                    allowed_size=allowed_rig_size
                )
        if tainted_items:
            raise RestrictionValidationError(tainted_items)

    @property
    def type(self):
        return Restriction.rig_size
