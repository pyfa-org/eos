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


from collections import namedtuple
from random import random

from eos.const.eos import EffectRunMode, State
from .base import BaseItemMixin


SideEffectData = namedtuple('SideEffectData', ('effect', 'chance', 'status'))


# Map which defines run mode into side-effect status conversion rules
# Format: {run mode: side-effect status}
mode_conv = {
    EffectRunMode.full_compliance: False,
    EffectRunMode.state_compliance: True,
    EffectRunMode.force_run: True,
    EffectRunMode.force_stop: False}


class SideEffectMixin(BaseItemMixin):
    """Allows to manage item's side-effects."""

    @property
    def side_effects(self):
        """Get map with data about item side-effects.

        Returns: Dictionary in {side-effect ID: (effect=effect object for this
        side-effect, chance=chance of setting in, enabled=side-effect status)}
        format.
        """
        side_effects = {}
        for effect_id, effect in self._eve_type_effects.items():
            # Effect must be from offline category
            if effect._state != State.offline:
                continue
            # Its application must be chance-based
            chance = effect.get_fitting_usage_chance(self)
            if chance is None:
                continue
            side_effect_state = mode_conv[self.get_effect_run_mode(effect_id)]
            side_effects[effect_id] = SideEffectData(
                effect, chance, side_effect_state)
        return side_effects

    def set_side_effect_status(self, effect_id, status):
        """Enable or disable side-effect.

        Args:
            effect_id: ID of side-effect.
            status: True for enabling, False for disabling.
        """
        if status:
            run_mode = EffectRunMode.state_compliance
        else:
            run_mode = EffectRunMode.full_compliance
        self.set_effect_run_mode(effect_id, run_mode)

    def randomize_side_effects(self):
        """Randomize side-effects' status according to chances to set in."""
        new_modes = {}
        for effect_id, edata in self.side_effects:
            # If it's supposed to be enabled, set state compliance mode, which
            # will keep effect running if item is in offline or higher state
            if random() < edata.chance:
                new_modes[effect_id] = EffectRunMode.state_compliance
            # If it should be disabled, full compliance will keep all chance-
            # based effects stopped
            else:
                new_modes[effect_id] = EffectRunMode.full_compliance
        self._set_effects_run_modes(new_modes)
