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


from eos.const.eos import State
from eos.fit.pubsub.message import (
    EffectsStarted, EffectsStopped, StatesActivated, StatesDeactivated)
from .base import BaseItemMixin


class ImmutableStateMixin(BaseItemMixin):
    """Supports immutable item states.

    That is, state can be defined at instantiation, and cannot be changed later.

    Args:
        state: State which should be used for item.

    Cooperative methods:
        __init__
    """

    def __init__(self, state, **kwargs):
        self.__state = state
        super().__init__(**kwargs)

    @property
    def state(self):
        """Access point to get item's state."""
        return self.__state


class MutableStateMixin(BaseItemMixin):
    """Supports mutable item states.

    Items based on this class will be able to change state after instantiation.

    Args:
        state: State which should be used for item initially.

    Cooperative methods:
        __init__
    """

    def __init__(self, state, **kwargs):
        self.__state = state
        super().__init__(**kwargs)

    @property
    def state(self):
        """Access point to get and set item's state."""
        return self.__state

    @state.setter
    def state(self, new_state):
        old_state = self.__state
        if new_state == old_state:
            return
        self.__state = new_state
        # When item is assigned to some fit, ask fit to perform fit-specific
        # state switch of our item
        fit = self._fit
        if fit is not None:
            if fit.source is not None:
                messages = []
                # State switching upwards
                if new_state > old_state:
                    states = {s for s in State if old_state < s <= new_state}
                    messages.append(StatesActivated(self, states))
                # State switching downwards
                else:
                    # Deactivate effects and states
                    states = {s for s in State if new_state < s <= old_state}
                    messages.append(StatesDeactivated(self, states))
                # Effect changes
                to_start, to_stop = self._get_wanted_effect_status_changes()
                if to_start:
                    self._running_effect_ids.update(to_start)
                    messages.append(EffectsStarted(self, to_start))
                if to_stop:
                    messages.append(EffectsStopped(self, to_stop))
                    self._running_effect_ids.difference_update(to_stop)
                fit._publish_bulk(messages)
            fit._volatile_mgr.clear_volatile_attrs()
