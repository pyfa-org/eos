# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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
from eos.fit.restriction_tracker.exception import RegisterValidationError
from .abc import RestrictionRegister


StateErrorData = namedtuple('StateErrorData', ('current_state', 'allowed_states'))


class StateRegister(RestrictionRegister):
    """
    Implements restriction:
    Verify that current state of holder is not bigger than
    max state its item allows (e.g. passive modules cannot be
    activated, active modules without overload effects cannot
    be overloaded, and so on).
    """

    def __init__(self):
        self.__holders = set()

    def register_holder(self, holder):
        # We're going to track all holders. Typically we track
        # online+ holders, as all holders can be at least offline
        self.__holders.add(holder)

    def unregister_holder(self, holder):
        self.__holders.discard(holder)

    def validate(self):
        tainted_holders = {}
        for holder in self.__holders:
            if holder.state > holder.item.max_state:
                allowed_states = tuple(filter(lambda s: s <= holder.item.max_state, State))
                tainted_holders[holder] = StateErrorData(
                    current_state=holder.state,
                    allowed_states=allowed_states
                )
        if tainted_holders:
            raise RegisterValidationError(tainted_holders)

    @property
    def restriction_type(self):
        return Restriction.state
