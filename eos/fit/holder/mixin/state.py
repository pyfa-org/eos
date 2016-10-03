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


from .holder import HolderBase


class ImmutableStateMixin(HolderBase):
    """
    Mixin intended to be used for holders which define
    state at instantiation time and do not change it later.

    Required arguments:
    state -- initial state to take

    Cooperative methods:
    __init__
    """

    def __init__(self, state, **kwargs):
        self.__state = state
        super().__init__(**kwargs)

    @property
    def state(self):
        return self.__state


class MutableStateMixin(HolderBase):
    """
    Mixin intended to be used for holders which can
    switch state at any time.

    Required arguments:
    state -- initial state to take

    Cooperative methods:
    __init__
    """

    def __init__(self, state, **kwargs):
        self.__state = state
        super().__init__(**kwargs)

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, new_state):
        if new_state == self.__state:
            return
        # When holder is assigned to some fit, ask fit to perform
        # fit-specific state switch of our holder
        fit = self._fit
        if fit is not None:
            fit._holder_state_switch(self, new_state)
        self.__state = new_state
