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

from eos.const.eos import Restriction
from eos.fit.item import Booster
from eos.fit.pubsub.message import InstrItemAdd, InstrItemRemove
from .base import BaseRestrictionRegister
from ..exception import RestrictionValidationError


BoosterEffectErrorData = namedtuple('BoosterEffectErrorData', ('illegally_disabled', 'disablable'))


class BoosterEffectRestrictionRegister(BaseRestrictionRegister):
    """
    Implements restriction:
    Booster must have all of its non-side-effects activable.

    If booster item has some side-effect disabled (set to blocked,
    or unactivable), it may become disabled regular effect when fit
    source is switched. Regular effects are not shown on booster
    side-effect API. Such effects are raised as an issue by this
    register.

    Details:
    Uses set of actually unactivable effects during validation,
    rather than set of IDs of effects which are unactivable.
    """

    def __init__(self, msg_broker):
        self.__boosters = set()
        msg_broker._subscribe(self, self._handler_map.keys())

    def _handle_item_addition(self, message):
        if isinstance(message.item, Booster):
            self.__boosters.add(message.item)

    def _handle_item_removal(self, message):
        self.__boosters.discard(message.item)

    _handler_map = {
        InstrItemAdd: _handle_item_addition,
        InstrItemRemove: _handle_item_removal
    }

    def validate(self):
        tainted_items = {}
        for booster in self.__boosters:
            # Check if any disabled effects cannot be found in
            # side-effect list
            disablable = set(booster.side_effects)
            illegal = set()
            for effect_id, effect_data in booster._effects_data.items():
                if effect_id in disablable:
                    continue
                if effect_data.activable is False:
                    illegal.add(effect_id)
            if len(illegal) == 0:
                continue
            tainted_items[booster] = BoosterEffectErrorData(
                illegally_disabled=illegal,
                disablable=disablable
            )
        if tainted_items:
            raise RestrictionValidationError(tainted_items)

    @property
    def type(self):
        return Restriction.booster_effect
