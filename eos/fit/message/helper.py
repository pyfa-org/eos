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


from eos.const.eos import EffectMode, State
from eos.const.eve import EffectId


from .message import (
    EffectsStarted, EffectsStopped, ItemAdded, ItemRemoved,
    StatesActivated, StatesDeactivated)


def get_items_added_messages(items):
    """Generate messages about new items.

    Args:
        items: Iterable with items which were added.

    Returns:
        Iterable with messages.
    """
    messages = []
    for item in items:
        # Item
        messages.append(ItemAdded(item))
        # States
        states = {s for s in State if s <= item.state}
        messages.append(StatesActivated(item, states))
        # Effects
        messages.extend(get_effects_status_update_messages(item))
    return messages


def get_items_removed_messages(items):
    """Generate messages about removed items.

    Args:
        items: Iterable with items which are to be removed.

    Returns:
        Iterable with messages.
    """
    messages = []
    for item in items:
        # Effects
        running_effect_ids = set(item._running_effect_ids)
        if running_effect_ids:
            messages.append(EffectsStopped(item, running_effect_ids))
            item._running_effect_ids.clear()
        # States
        states = {s for s in State if s <= item.state}
        messages.append(StatesDeactivated(item, states))
        # Item
        messages.append(ItemRemoved(item))
    return messages


def get_item_state_update_messages(item, old_state, new_state):
    """Generate messages about changed item state.

    Args:
        item: Item which had its state changed.
        old_state: Old state of the item.
        new_state: New state of the item.

    Returns:
        Iterable with messages.
    """
    messages = []
    # State switching upwards
    if new_state > old_state:
        states = {s for s in State if old_state < s <= new_state}
        messages.append(StatesActivated(item, states))
    # State switching downwards
    else:
        states = {s for s in State if new_state < s <= old_state}
        messages.append(StatesDeactivated(item, states))
    # Effects
    messages.extend(get_effects_status_update_messages(item))
    return messages


def get_effects_status_update_messages(item):
    """Generate messages about changed effect statuses.

    Besides generating messages, it actually updates item's set of effects which
    are considered as running.

    Args:
        item: Item for which effect status updates is requested.

    Returns:
        Iterable with messages.
    """
    messages = []
    to_start, to_stop = _get_wanted_effect_status_changes(item)
    if to_start:
        item._running_effect_ids.update(to_start)
        messages.append(EffectsStarted(item, to_start))
    if to_stop:
        messages.append(EffectsStopped(item, to_stop))
        item._running_effect_ids.difference_update(to_stop)
    return messages


def _get_wanted_effect_status_changes(item):
    """Get changes needed to actualize effect running statuses.

    Args:
        item: Item for which effects are to be actualized.

    Returns:
        Two sets, first with effect IDs which should be started and second with
        effect IDs which should be stopped to achieve proper state.
    """
    effects = item._type_effects
    # Set of effects which should be running according to new conditions
    new_running_effect_ids = set()
    # Process 'online' effect separately, as it's needed for all other effects
    # from online categories
    if EffectId.online in effects:
        online_running = _get_wanted_effect_status(
            item, effects[EffectId.online], None)
        if online_running is True:
            new_running_effect_ids.add(EffectId.online)
    else:
        online_running = False
    # Do a pass over regular effects
    for effect_id, effect in effects.items():
        if effect_id == EffectId.online:
            continue
        if _get_wanted_effect_status(item, effect, online_running):
            new_running_effect_ids.add(effect_id)
    to_start = new_running_effect_ids.difference(item._running_effect_ids)
    to_stop = item._running_effect_ids.difference(new_running_effect_ids)
    return to_start, to_stop


def _get_wanted_effect_status(item, effect, online_running):
    """Decide if an effect should be running or not.

    Decision is taken based on effect's run mode, item's state and multiple less
    significant factors.

    Args:
        item: Item which should carry the effect.
        effect: The effect in question.
        online_running: Flag which tells function if 'online' effect is running
            on the item or not.

    Returns:
        Boolean flag, True when effect should be running, False when it should
        not.
    """
    # Decide how we handle effect based on its run mode
    effect_mode = item.get_effect_mode(effect.id)
    if effect_mode == EffectMode.full_compliance:
        # Check state restriction first, as it should be checked regardless of
        # effect category
        effect_state = effect._state
        if item.state < effect_state:
            return False
        # Offline effects must NOT specify fitting usage chance
        if effect_state == State.offline:
            return effect.fitting_usage_chance_attribute_id is None
        # Online effects depend on 'online' effect
        elif effect_state == State.online:
            # If we've been requested 'online' effect status, it has no
            # additional restrictions
            if effect.id == EffectId.online:
                return True
            # For regular online effects, check if 'online' is running
            else:
                return online_running
        # Only default active effect is run in full compliance
        elif effect_state == State.active:
            return item._type_default_effect is effect
        # No additional restrictions for overload effects
        elif effect_state == State.overload:
            return True
        # For safety, generally should never happen
        else:
            return False
    # In state compliance, consider effect running if item's state is at least
    # as high as required by the effect
    elif effect_mode == EffectMode.state_compliance:
        return item.state >= effect._state
    # If it's supposed to always run, make it so without a second thought
    elif effect_mode == EffectMode.force_run:
        return True
    # Same for always-stop
    elif effect_mode == EffectMode.force_stop:
        return False
    # For safety, generally should never happen
    else:
        return False
