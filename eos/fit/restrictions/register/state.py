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

from eos.const.eos import Restriction, State
from .base import BaseRestrictionRegister
from ..exception import RegisterValidationError


StateErrorData = namedtuple('StateErrorData', ('current_state', 'allowed_states'))


class StateRestrictionRegister(BaseRestrictionRegister):
    """
    Implements restriction:
    Verify that current state of item is not bigger than max state
    its eve type allows (e.g. passive modules cannot be activated,
    active modules without overload effects cannot be overloaded,
    and so on).
    """

    def __init__(self):
        self.__items = set()

    def register_item(self, item):
        # We're going to track all items. Typically we track
        # online+ items, as all items can be at least offline
        self.__items.add(item)

    def unregister_item(self, item):
        self.__items.discard(item)

    def validate(self):
        tainted_items = {}
        for item in self.__items:
            if item.state > item._eve_type.max_state:
                allowed_states = tuple(filter(lambda s: s <= item._eve_type.max_state, State))
                tainted_items[item] = StateErrorData(
                    current_state=item.state,
                    allowed_states=allowed_states
                )
        if tainted_items:
            raise RegisterValidationError(tainted_items)

    @property
    def restriction_type(self):
        return Restriction.state
