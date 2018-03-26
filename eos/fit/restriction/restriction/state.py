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
from eos.const.eos import State
from eos.fit.item.charge import Autocharge
from eos.fit.item.charge import Charge
from eos.fit.message import StatesActivatedLoaded
from eos.fit.message import StatesDeactivatedLoaded
from .base import BaseRestrictionRegister
from ..exception import RestrictionValidationError


StateErrorData = namedtuple(
    'StateErrorData', ('state', 'allowed_states'))

EXCEPTIONS = (Charge, Autocharge)


class StateRestrictionRegister(BaseRestrictionRegister):
    """Make sure items' states are consistent.

    I.e. check that passive modules are not active, etc.
    """

    type = Restriction.state

    def __init__(self, fit):
        self.__restricted_items = set()
        fit._subscribe(self, self._handler_map.keys())

    def _handle_states_activated_loaded(self, msg):
        if State.online in msg.states and not isinstance(msg.item, EXCEPTIONS):
            self.__restricted_items.add(msg.item)

    def _handle_states_deactivated_loaded(self, msg):
        if State.online in msg.states:
            self.__restricted_items.discard(msg.item)

    _handler_map = {
        StatesActivatedLoaded: _handle_states_activated_loaded,
        StatesDeactivatedLoaded: _handle_states_deactivated_loaded}

    def validate(self):
        tainted_items = {}
        for item in self.__restricted_items:
            if item.state > item._type.max_state:
                allowed_states = tuple(
                    s for s in State if s <= item._type.max_state)
                tainted_items[item] = StateErrorData(
                    state=item.state,
                    allowed_states=allowed_states)
        if tainted_items:
            raise RestrictionValidationError(tainted_items)
