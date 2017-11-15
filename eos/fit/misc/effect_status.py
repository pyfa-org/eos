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


from logging import getLogger

from eos.const.eos import EffectMode, State
from eos.const.eve import EffectId


logger = getLogger(__name__)


class EffectStatusResolver:

    @staticmethod
    def get_effect_status_updates(item):
        """Get changes needed to actualize effect running statuses.

        Args:
            item: Item for which effects are to be actualized.

        Returns:
            Two sets, first with effect IDs which should be started and second
            with effect IDs which should be stopped to achieve proper state.
        """
        effects = item._type_effects
        # Set of effects which should be running according to new conditions
        new_running_effect_ids = set()
        # Process 'online' effect separately, as it's needed for all other
        # effects from online categories
        if EffectId.online in effects:
            online_running = EffectStatusResolver.resolve_effect_status(
                item, effects[EffectId.online], None)
            if online_running:
                new_running_effect_ids.add(EffectId.online)
        else:
            online_running = False
        # Do a pass over regular effects
        for effect_id, effect in effects.items():
            if effect_id == EffectId.online:
                continue
            if EffectStatusResolver.resolve_effect_status(
                item, effect, online_running
            ):
                new_running_effect_ids.add(effect_id)
        start_ids = new_running_effect_ids.difference(item._running_effect_ids)
        stop_ids = item._running_effect_ids.difference(new_running_effect_ids)
        return start_ids, stop_ids

    @staticmethod
    def resolve_effect_status(item, effect, online_running):
        """Decide if an effect should be running or not.

        Decision is taken based on effect's run mode, item's state and multiple
        less significant factors.

        Args:
            item: Item which should carry the effect.
            effect: The effect in question.
            online_running: Flag which tells function if 'online' effect is
                running on the item or not.

        Returns:
            Boolean flag, True when effect should be running, False when it
            should not.
        """
        resolver_map = {
            EffectMode.full_compliance:
                EffectStatusResolver._resolve_full_compliance,
            EffectMode.state_compliance:
                EffectStatusResolver._resolve_state_compliance,
            EffectMode.force_run:
                EffectStatusResolver._resolve_force_run,
            EffectMode.force_stop:
                EffectStatusResolver._resolve_force_stop}
        # Decide how we handle effect based on its run mode
        effect_mode = item.get_effect_mode(effect.id)
        try:
            resolver = resolver_map[effect_mode]
        except KeyError:
            msg = 'unknown effect mode {}'.format(effect_mode)
            logger.warning(msg)
            return False
        else:
            return resolver(item, effect, online_running)

    @staticmethod
    def _resolve_full_compliance(item, effect, online_running):
        # Check state restriction first, as it should be checked regardless of
        # effect category
        effect_state = effect._state
        if item.state < effect_state:
            return False
        # Offline effects must NOT specify fitting usage chance
        if effect_state == State.offline:
            return effect.fitting_usage_chance_attr_id is None
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

    @staticmethod
    def _resolve_state_compliance(item, effect, _):
        # In state compliance, consider effect running if item's state is at
        # least as high as required by the effect
        return item.state >= effect._state

    @staticmethod
    def _resolve_force_run(*_):
        return True

    @staticmethod
    def _resolve_force_stop(*_):
        return False
