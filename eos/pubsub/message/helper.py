# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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


from copy import copy

from eos.const.eos import State
from eos.effect_status import EffectStatusResolver
from .item import ItemAdded
from .item import ItemRemoved
from .item import StatesActivated
from .item import StatesDeactivated
from .item_loaded import EffectApplied
from .item_loaded import EffectUnapplied
from .item_loaded import EffectsStarted
from .item_loaded import EffectsStopped
from .item_loaded import ItemLoaded
from .item_loaded import ItemUnloaded
from .item_loaded import StatesActivatedLoaded
from .item_loaded import StatesDeactivatedLoaded


class MsgHelper:
    """Assists with generation of messages."""

    @staticmethod
    def get_item_added_msgs(item):
        """Generate messages about added item."""
        msgs = []
        # Item
        msgs.append(ItemAdded(item))
        # States
        states = {s for s in State if s <= item.state}
        msgs.append(StatesActivated(item, states))
        return msgs

    @staticmethod
    def get_item_removed_msgs(item):
        """Generate messages about item being removed."""
        msgs = []
        # States
        states = {s for s in State if s <= item.state}
        msgs.append(StatesDeactivated(item, states))
        # Item
        msgs.append(ItemRemoved(item))
        return msgs

    @staticmethod
    def get_item_loaded_msgs(item):
        """Generate messages about loaded item."""
        msgs = []
        # Item
        msgs.append(ItemLoaded(item))
        # States
        states = {s for s in State if s <= item.state}
        msgs.append(StatesActivatedLoaded(item, states))
        # Effects
        msgs.extend(MsgHelper.get_effects_status_update_msgs(item))
        return msgs

    @staticmethod
    def get_item_unloaded_msgs(item):
        """Generate messages about unloaded item."""
        msgs = []
        # Effects
        running_effect_ids = item._running_effect_ids
        if running_effect_ids:
            # Unapply effects before stopping them
            tgt_getter = getattr(item, '_get_effects_tgts', None)
            if tgt_getter:
                effects_tgts = tgt_getter(running_effect_ids)
                for effect_id, tgt_items in effects_tgts.items():
                    msgs.append(EffectUnapplied(item, effect_id, tgt_items))
            # Stop effects
            # Copy running effect IDs container, because we clear it on the next
            # line but it will be processed by message subscribers much later
            msgs.append(EffectsStopped(item, copy(running_effect_ids)))
            running_effect_ids.clear()
        # States
        states = {s for s in State if s <= item.state}
        msgs.append(StatesDeactivatedLoaded(item, states))
        # Item
        msgs.append(ItemUnloaded(item))
        return msgs

    @staticmethod
    def get_item_state_update_msgs(item, old_state, new_state):
        """Generate messages about changed item state."""
        msgs = []
        # State switching upwards
        if new_state > old_state:
            states = {s for s in State if old_state < s <= new_state}
            msgs.append(StatesActivated(item, states))
            if item._is_loaded:
                msgs.append(StatesActivatedLoaded(item, states))
        # State switching downwards
        else:
            states = {s for s in State if new_state < s <= old_state}
            if item._is_loaded:
                msgs.append(StatesDeactivatedLoaded(item, states))
            msgs.append(StatesDeactivated(item, states))
        # Effects
        if item._is_loaded:
            msgs.extend(MsgHelper.get_effects_status_update_msgs(item))
        return msgs

    @staticmethod
    def get_effects_status_update_msgs(item):
        """Generate messages about changed effect statuses.

        Besides generating messages, it actually updates item's set of effects
        which are considered as running.
        """
        # Set of effects which should be running according to new conditions
        new_running_effect_ids = set()
        effects_status = EffectStatusResolver.resolve_effects_status(item)
        for effect_id, status in effects_status.items():
            if status:
                new_running_effect_ids.add(effect_id)
        start_ids = new_running_effect_ids.difference(item._running_effect_ids)
        stop_ids = item._running_effect_ids.difference(new_running_effect_ids)
        msgs = []
        if start_ids:
            item._running_effect_ids.update(start_ids)
            # Start effects
            msgs.append(EffectsStarted(item, start_ids))
            # Apply effects to targets
            tgt_getter = getattr(item, '_get_effects_tgts', None)
            if tgt_getter:
                effects_tgts = tgt_getter(start_ids)
                for effect_id, tgt_items in effects_tgts.items():
                    msgs.append(EffectApplied(item, effect_id, tgt_items))
        if stop_ids:
            # Unapply effects from targets
            tgt_getter = getattr(item, '_get_effects_tgts', None)
            if tgt_getter:
                effects_tgts = tgt_getter(stop_ids)
                for effect_id, tgt_items in effects_tgts.items():
                    msgs.append(EffectUnapplied(item, effect_id, tgt_items))
            # Stop effects
            msgs.append(EffectsStopped(item, stop_ids))
            item._running_effect_ids.difference_update(stop_ids)
        return msgs
