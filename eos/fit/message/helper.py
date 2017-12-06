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
from eos.fit.misc.effect_status import EffectStatusResolver
from .message import EffectsStarted
from .message import EffectsStopped
from .message import ItemAdded
from .message import ItemRemoved
from .message import StatesActivated
from .message import StatesDeactivated


class MsgHelper:
    """Assists with generation of messages for various complex needs."""

    @staticmethod
    def get_items_added_msgs(items):
        """Generate messages about new items.

        Args:
            items: Iterable with items which were added.

        Returns:
            Iterable with messages.
        """
        msgs = []
        for item in items:
            # Item
            msgs.append(ItemAdded(item))
            # States
            states = {s for s in State if s <= item.state}
            msgs.append(StatesActivated(item, states))
            # Effects
            msgs.extend(MsgHelper.get_effects_status_update_msgs(item))
        return msgs

    @staticmethod
    def get_items_removed_msgs(items):
        """Generate messages about removed items.

        Args:
            items: Iterable with items which are to be removed.

        Returns:
            Iterable with messages.
        """
        msgs = []
        for item in items:
            # Effects
            running_effect_ids = item._running_effect_ids
            if running_effect_ids:
                # Copy set to make sure messages keep full data despite it being
                # cleared on the next line
                msgs.append(EffectsStopped(item, set(running_effect_ids)))
                running_effect_ids.clear()
            # States
            states = {s for s in State if s <= item.state}
            msgs.append(StatesDeactivated(item, states))
            # Item
            msgs.append(ItemRemoved(item))
        return msgs

    @staticmethod
    def get_item_state_update_msgs(item, old_state, new_state):
        """Generate messages about changed item state.

        Args:
            item: Item which had its state changed.
            old_state: Old state of the item.
            new_state: New state of the item.

        Returns:
            Iterable with messages.
        """
        msgs = []
        # State switching upwards
        if new_state > old_state:
            states = {s for s in State if old_state < s <= new_state}
            msgs.append(StatesActivated(item, states))
        # State switching downwards
        else:
            states = {s for s in State if new_state < s <= old_state}
            msgs.append(StatesDeactivated(item, states))
        # Effects
        msgs.extend(MsgHelper.get_effects_status_update_msgs(item))
        return msgs

    @staticmethod
    def get_effects_status_update_msgs(item):
        """Generate messages about changed effect statuses.

        Besides generating messages, it actually updates item's set of effects
        which are considered as running.

        Args:
            item: Item for which effect status updates is requested.

        Returns:
            Iterable with messages.
        """
        msgs = []
        start_ids, stop_ids = (
            EffectStatusResolver.get_effect_status_updates(item))
        if start_ids:
            item._running_effect_ids.update(start_ids)
            msgs.append(EffectsStarted(item, start_ids))
        if stop_ids:
            msgs.append(EffectsStopped(item, stop_ids))
            item._running_effect_ids.difference_update(stop_ids)
        return msgs
