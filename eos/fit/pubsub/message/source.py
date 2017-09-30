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
from .item import (
    InstrItemAdd, InstrItemRemove, InstrStatesActivate, InstrStatesDeactivate,
    InstrEffectsStart, InstrEffectsStop
)


class InputSourceChanged(BaseInputMessage):

    def __init__(self, old, new, items):
        self.old = old
        self.new = new
        self.items = items

    def get_instructions(self):
        instructions = []
        # Issue instructions to remove items, if there was an old source
        if self.old is not None:
            for item in self.items:
                states = {s for s in State if s <= item.state}
                # Handle effect deactivation
                running_effects_copy = set(item._running_effects)
                if len(running_effects_copy) > 0:
                    instructions.append(InstrEffectsStop(item, running_effects_copy))
                    item._running_effects.clear()
                # Handle state deactivation
                instructions.append(InstrStatesDeactivate(item, states))
                # Handle item removal
                instructions.append(InstrItemRemove(item))
        # Force refresh of all source-dependent objects
        instructions.append(InstrRefreshSource())
        # Issue instructions to add items again, if there's a new source
        if self.new is not None:
            for item in self.items:
                # Handle item addition
                instructions.append(InstrItemAdd(item))
                # Handle state activation
                states = {s for s in State if s <= item.state}
                instructions.append(InstrStatesActivate(item, states))
                # Handle effect activation
                to_start_effects, to_stop_effects = item._get_wanted_effect_run_status_changes()
                if len(to_start_effects) > 0:
                    item._running_effects.update(to_start_effects)
                    instructions.append(InstrEffectsStart(item, to_start_effects))
                if len(to_stop_effects) > 0:
                    instructions.append(InstrEffectsStop(item, to_stop_effects))
                    item._running_effects.difference_update(to_stop_effects)
        return instructions

    def __repr__(self):
        spec = ['old', 'new', 'items']
        return make_repr_str(self, spec)


class InstrRefreshSource(BaseInstructionMessage):
    ...
