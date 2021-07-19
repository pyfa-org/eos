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


from logging import getLogger

from eos.const.eos import EffectMode
from eos.const.eos import State
from eos.const.eve import EffectId


logger = getLogger(__name__)


class EffectStatusResolver:

    @staticmethod
    def resolve_effect_status(item, effect_id, state_override=None):
        effects_status = EffectStatusResolver.resolve_effects_status(
            item, [effect_id], state_override)
        return effects_status[effect_id]

    @staticmethod
    def resolve_effects_status(item, effect_ids=None, state_override=None):
        """Decide if effects should be running or not.

        Decision is taken based on effect's run mode, item's state and multiple
        less significant factors.

        Args:
            item: Item which should carry the effects.
            effect_ids (optional): Iterable with effect IDs in question. When
                not specified, status of all item effects is resolved.
            state_override (optional): Use this state instead of item's actual
                state. By default, item's state is used.

        Returns:
            Resolved effect statuses in {effect ID: status} format. Status is
            boolean flag, True when effect should be running, False when it
            should not.
        """
        item_effects = item._type_effects
        if effect_ids is None:
            rq_effect_ids = set(item_effects)
        else:
            rq_effect_ids = set(effect_ids).intersection(item_effects)
        effects_status = {}
        # Process 'online' effect separately, as it's needed for all other
        # effects from online categories
        if EffectId.online in item_effects:
            online_running = EffectStatusResolver.__resolve_effect_status(
                item, item_effects[EffectId.online], None, state_override)
            if EffectId.online in rq_effect_ids:
                effects_status[EffectId.online] = online_running
        else:
            online_running = False
        # Process the rest of effects
        for effect_id in rq_effect_ids:
            if effect_id == EffectId.online:
                continue
            effect = item_effects[effect_id]
            effect_status = EffectStatusResolver.__resolve_effect_status(
                item, effect, online_running, state_override)
            effects_status[effect_id] = effect_status
        return effects_status

    @staticmethod
    def __resolve_effect_status(item, effect, online_running, state_override):
        resolver_map = {
            EffectMode.full_compliance:
                EffectStatusResolver.__resolve_full_compliance,
            EffectMode.state_compliance:
                EffectStatusResolver.__resolve_state_compliance,
            EffectMode.force_run:
                EffectStatusResolver.__resolve_force_run,
            EffectMode.force_stop:
                EffectStatusResolver.__resolve_force_stop}
        # Decide how we handle effect based on its run mode
        effect_mode = item.get_effect_mode(effect.id)
        try:
            resolver = resolver_map[effect_mode]
        except KeyError:
            msg = 'unknown effect mode {}'.format(effect_mode)
            logger.warning(msg)
            return False
        else:
            return resolver(item, effect, online_running, state_override)

    @staticmethod
    def __resolve_full_compliance(item, effect, online_running, state_override):
        if state_override is not None:
            item_state = state_override
        else:
            item_state = item.state
        # Check state restriction first, as it should be checked regardless of
        # effect category
        effect_state = effect._state
        if item_state < effect_state:
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
    def __resolve_state_compliance(item, effect, _, state_override):
        if state_override is not None:
            item_state = state_override
        else:
            item_state = item.state
        # In state compliance, consider effect running if item's state is at
        # least as high as required by the effect
        return item_state >= effect._state

    @staticmethod
    def __resolve_force_run(*_):
        return True

    @staticmethod
    def __resolve_force_stop(*_):
        return False
