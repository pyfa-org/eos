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
from .base import BaseInputMessage, BaseInstructionMessage


class InputItemAdded(BaseInputMessage):

    def __init__(self, item, position):
        self.item = item
        self.position = position

    def get_instructions(self):
        # Do nothing if fit doesn't have source
        if self.item._fit.source is None:
            return ()
        instructions = []
        # Handle item addition
        instructions.append(InstrItemAdd(self.item, self.position))
        # Handle state activation
        states = {s for s in State if s <= self.item.state}
        instructions.append(InstrStatesActivate(self.item, states))
        # Handle effect activation
        effects = {eid for eid, e in self.item._activable_effects.items() if e._state in states}
        if len(effects) > 0:
            instructions.append(InstrEffectsActivate(self.item, effects))
        return instructions

    def __repr__(self):
        spec = ['item', 'position']
        return make_repr_str(self, spec)


class InputItemRemoved(BaseInputMessage):

    def __init__(self, item):
        self.item = item

    def get_instructions(self):
        # Do nothing if fit doesn't have source
        if self.item._fit.source is None:
            return ()
        instructions = []
        states = {s for s in State if s <= self.item.state}
        # Handle effect deactivation
        effects = {eid for eid, e in self.item._activable_effects.items() if e._state in states}
        if len(effects) > 0:
            instructions.append(InstrEffectsDeactivate(self.item, effects))
        # Handle state deactivation
        instructions.append(InstrStatesDeactivate(self.item, states))
        # Handle item removal
        instructions.append(InstrItemRemove(self.item))
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
        # Do nothing if fit doesn't have source
        if self.item._fit.source is None:
            return ()
        instructions = []
        # State switching upwards
        if self.new > self.old:
            # Activate states and effects, which are activable and should be activated
            # together with activated states
            states = {s for s in State if self.old < s <= self.new}
            effects = {eid for eid, e in self.item._activable_effects.items() if e._state in states}
            instructions.append(InstrStatesActivate(self.item, states))
            if len(effects) > 0:
                instructions.append(InstrEffectsActivate(self.item, effects))
        # State switching downwards
        elif self.new < self.old:
            # Deactivate effects and states
            states = {s for s in State if self.new < s <= self.old}
            effects = {eid for eid, e in self.item._activable_effects.items() if e._state in states}
            if len(effects) > 0:
                instructions.append(InstrEffectsDeactivate(self.item, effects))
            instructions.append(InstrStatesDeactivate(self.item, states))
        return instructions

    def __repr__(self):
        spec = ['item', 'old', 'new']
        return make_repr_str(self, spec)


class InputEffectsStatusChanged(BaseInputMessage):

    def __init__(self, item, effects):
        self.item = item
        # Format: {effect ID: status}
        self.effects = effects

    def get_instructions(self):
        # Do nothing if fit doesn't have source
        if self.item._fit.source is None:
            return ()
        instructions = []
        # If there're effects set for activation, issue activation command
        activate = tuple(e for e in self.effects if self.effects[e])
        if len(activate) > 0:
            instructions.append(InstrEffectsActivate(self.item, activate))
        # Same for deactivation
        deactivate = tuple(e for e in self.effects if not self.effects[e])
        if len(deactivate) > 0:
            instructions.append(InstrEffectsDeactivate(self.item, deactivate))
        return instructions

    def __repr__(self):
        spec = ['item', 'effects']
        return make_repr_str(self, spec)


class InputItemsPositionChanged(BaseInputMessage):

    def __init__(self, positions):
        # Format: {item: new position}
        self.positions = positions

    def get_instructions(self):
        instructions = []
        for item, position in self.positions.items():
            # Do nothing if item's fit doesn't have source
            if item._fit.source is None:
                return ()
            instructions.append(InstrItemPositionChange(item, position))
        return instructions

    def __repr__(self):
        spec = ['positions']
        return make_repr_str(self, spec)


class InstrItemAdd(BaseInstructionMessage):

    def __init__(self, item, position):
        self.item = item
        self.position = position

    def __repr__(self):
        spec = ['item', 'position']
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


class InstrEffectsActivate(BaseInstructionMessage):

    def __init__(self, item, effects):
        self.item = item
        # Format: {effect IDs}
        self.effects = effects

    def __repr__(self):
        spec = ['item', 'effects']
        return make_repr_str(self, spec)


class InstrEffectsDeactivate(BaseInstructionMessage):

    def __init__(self, item, effects):
        self.item = item
        # Format: {effect IDs}
        self.effects = effects

    def __repr__(self):
        spec = ['item', 'effects']
        return make_repr_str(self, spec)


class InstrItemPositionChange(BaseInstructionMessage):

    def __init__(self, item, position):
        self.item = item
        self.position = position

    def __repr__(self):
        spec = ['item', 'position']
        return make_repr_str(self, spec)
