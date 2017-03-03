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


from eos.const.eos import State
from eos.util.repr import make_repr_str
from .base import BaseMessage


class ItemAdded(BaseMessage):

    def __init__(self, item, source_switch=False):
        self.item = item
        self.source_switch = source_switch

    def expand(self):
        states_msg = StatesActivated(self.item, states=tuple(filter(lambda s: s <= self.item.state, State)))
        effects_msg = EffectsActivated(self.item, effects=tuple(self.item._active_effects))
        return (self, states_msg, effects_msg)

    def __repr__(self):
        spec = ['item', 'source_switch']
        return make_repr_str(self, spec)


class ItemRemoved(BaseMessage):

    def __init__(self, item, source_switch=False):
        self.item = item
        self.source_switch = source_switch

    def expand(self):
        effects_msg = EffectsDeactivated(self.item, effects=tuple(self.item._active_effects))
        states_msg = StatesDeactivated(self.item, states=tuple(s for s in State if s <= self.item.state))
        return (effects_msg, states_msg, self)

    def __repr__(self):
        spec = ['item', 'source_switch']
        return make_repr_str(self, spec)


class StatesActivated(BaseMessage):

    def __init__(self, item, states):
        self.item = item
        self.states = states

    def expand(self):
        effects = tuple(e.id for e in self.item._active_effects.values if e._state in self.states)
        effects_msg = EffectsActivated(self.item, effects=effects)
        return (self, effects_msg)

    def __repr__(self):
        spec = ['item', 'states']
        return make_repr_str(self, spec)


class StatesDeactivated(BaseMessage):
    def __init__(self, item, states):
        self.item = item
        self.states = states

    def expand(self):
        effects = tuple(e.id for e in self.item._active_effects.values if e._state in self.states)
        effects_msg = EffectsDeactivated(self.item, effects=effects)
        return (effects_msg, self)

    def __repr__(self):
        spec = ['item', 'states']
        return make_repr_str(self, spec)


class EffectsActivated(BaseMessage):

    def __init__(self, item, effects):
        self.item = item
        self.effects = effects

    def __repr__(self):
        spec = ['item', 'effects']
        return make_repr_str(self, spec)


class EffectsDeactivated(BaseMessage):

    def __init__(self, item, effects):
        self.item = item
        self.effects = effects

    def __repr__(self):
        spec = ['item', 'effects']
        return make_repr_str(self, spec)
