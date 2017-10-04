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
from eos.util.repr import make_repr_str
from .base import BaseInputMessage, BaseInstructionMessage


class InputItemAdded(BaseInputMessage):

    def __init__(self, item):
        self.item = item

    def get_instructions(self):
        item = self.item
        # Do nothing if fit doesn't have source
        if item._fit.source is None:
            return ()
        instructions = []
        # Handle item addition
        instructions.append(InstrItemAdd(item))
        # Handle state activation
        states = {s for s in State if s <= item.state}
        instructions.append(InstrStatesActivate(item, states))
        # Handle effect activation
        to_start_effects, to_stop_effects = item._get_wanted_effect_run_status_changes()
        if to_start_effects:
            item._running_effects.update(to_start_effects)
            instructions.append(InstrEffectsStart(item, to_start_effects))
        if to_stop_effects:
            instructions.append(InstrEffectsStop(item, to_stop_effects))
            item._running_effects.difference_update(to_stop_effects)
        return instructions

    def __repr__(self):
        spec = ['item']
        return make_repr_str(self, spec)


class InputItemRemoved(BaseInputMessage):

    def __init__(self, item):
        self.item = item

    def get_instructions(self):
        item = self.item
        # Do nothing if fit doesn't have source
        if item._fit.source is None:
            return ()
        instructions = []
        states = {s for s in State if s <= item.state}
        # Handle effect deactivation
        running_effects_copy = set(item._running_effects)
        if running_effects_copy:
            instructions.append(InstrEffectsStop(item, running_effects_copy))
            item._running_effects.clear()
        # Handle state deactivation
        instructions.append(InstrStatesDeactivate(item, states))
        # Handle item removal
        instructions.append(InstrItemRemove(item))
        return instructions

    def __repr__(self):
        spec = ['item']
        return make_repr_str(self, spec)


class InputStateChanged(BaseInputMessage):

    def __init__(self, item, old, new):
        self.item = item
        self.old = old
        self.new = new

    def get_instructions(self):
        item = self.item
        # Do nothing if fit doesn't have source
        if item._fit.source is None:
            return ()
        instructions = []
        # State switching upwards
        if self.new > self.old:
            states = {s for s in State if self.old < s <= self.new}
            instructions.append(InstrStatesActivate(item, states))
        # State switching downwards
        else:
            # Deactivate effects and states
            states = {s for s in State if self.new < s <= self.old}
            instructions.append(InstrStatesDeactivate(item, states))
        # Effect changes
        to_start_effects, to_stop_effects = item._get_wanted_effect_run_status_changes()
        if to_start_effects:
            item._running_effects.update(to_start_effects)
            instructions.append(InstrEffectsStart(item, to_start_effects))
        if to_stop_effects:
            instructions.append(InstrEffectsStop(item, to_stop_effects))
            item._running_effects.difference_update(to_stop_effects)
        return instructions

    def __repr__(self):
        spec = ['item', 'old', 'new']
        return make_repr_str(self, spec)


class InputEffectsRunModeChanged(BaseInputMessage):

    def __init__(self, item):
        self.item = item

    def get_instructions(self):
        item = self.item
        # Do nothing if fit doesn't have source
        if item._fit.source is None:
            return ()
        instructions = []
        to_start_effects, to_stop_effects = item._get_wanted_effect_run_status_changes()
        if to_start_effects:
            item._running_effects.update(to_start_effects)
            instructions.append(InstrEffectsStart(item, to_start_effects))
        if to_stop_effects:
            instructions.append(InstrEffectsStop(item, to_stop_effects))
            item._running_effects.difference_update(to_stop_effects)
        return instructions

    def __repr__(self):
        spec = ['item']
        return make_repr_str(self, spec)


class InstrItemAdd(BaseInstructionMessage):

    def __init__(self, item):
        self.item = item

    def __repr__(self):
        spec = ['item']
        return make_repr_str(self, spec)


class InstrItemRemove(BaseInstructionMessage):

    def __init__(self, item):
        self.item = item

    def __repr__(self):
        spec = ['item']
        return make_repr_str(self, spec)


class InstrStatesActivate(BaseInstructionMessage):

    def __init__(self, item, states):
        self.item = item
        # Format: {states}
        self.states = states

    def __repr__(self):
        spec = ['item', 'states']
        return make_repr_str(self, spec)


class InstrStatesDeactivate(BaseInstructionMessage):

    def __init__(self, item, states):
        self.item = item
        # Format: {states}
        self.states = states

    def __repr__(self):
        spec = ['item', 'states']
        return make_repr_str(self, spec)


class InstrEffectsStart(BaseInstructionMessage):

    def __init__(self, item, effects):
        self.item = item
        # Format: {effect IDs}
        self.effects = effects

    def __repr__(self):
        spec = ['item', 'effects']
        return make_repr_str(self, spec)


class InstrEffectsStop(BaseInstructionMessage):

    def __init__(self, item, effects):
        self.item = item
        # Format: {effect IDs}
        self.effects = effects

    def __repr__(self):
        spec = ['item', 'effects']
        return make_repr_str(self, spec)
