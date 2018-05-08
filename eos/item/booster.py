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


from collections import namedtuple
from random import random

from eos.const.eos import EffectMode
from eos.const.eos import ModDomain
from eos.const.eos import State
from eos.const.eve import AttrId
from eos.effect_status import EffectStatusResolver
from eos.util.repr import make_repr_str
from .exception import NoSuchSideEffectError
from .mixin.state import ImmutableStateMixin


SIDE_EFFECT_STATE = State.offline


SideEffectData = namedtuple('SideEffectData', ('chance', 'status'))


class Booster(ImmutableStateMixin):
    """Represents a booster.

    Args:
        type_id: Identifier of item type which should serve as base for this
            booster.
    """

    def __init__(self, type_id):
        super().__init__(type_id=type_id, state=State.offline)

    # Side-effect-related methods
    @property
    def side_effects(self):
        """Get map with data about item side-effects.

        Returns:
            Dictionary in {effect ID: (effect=effect, chance=chance of setting
            in, enabled=side-effect status)} format.
        """
        chances = self.__side_effect_chances
        statuses = EffectStatusResolver.resolve_effects_status(
            self, chances.keys(), state_override=SIDE_EFFECT_STATE)
        side_effects = {}
        for effect_id, chance in chances.items():
            status = statuses[effect_id]
            side_effects[effect_id] = SideEffectData(chance, status)
        return side_effects

    def set_side_effect_status(self, effect_id, status):
        """Enable or disable side-effect.

        Args:
            effect_id: ID of side-effect.
            status: True for enabling, False for disabling.
        """
        if effect_id not in self.__side_effect_chances:
            raise NoSuchSideEffectError(effect_id)
        if status:
            effect_mode = EffectMode.state_compliance
        else:
            effect_mode = EffectMode.full_compliance
        self.set_effect_mode(effect_id, effect_mode)

    def randomize_side_effects(self):
        """Randomize side-effects' status according to chances to set in."""
        new_modes = {}
        for effect_id, chance in self.__side_effect_chances:
            # If it's supposed to be enabled, set state compliance mode, which
            # will keep effect running if item is in offline or higher state
            if random() < chance:
                new_modes[effect_id] = EffectMode.state_compliance
            # If it should be disabled, full compliance will keep all chance-
            # based effects stopped
            else:
                new_modes[effect_id] = EffectMode.full_compliance
        self._set_effects_modes(new_modes)

    @property
    def __side_effect_chances(self):
        side_effect_chances = {}
        for effect_id, effect in self._type_effects.items():
            # Effect must be from offline category
            if effect._state != SIDE_EFFECT_STATE:
                continue
            # Its application must be chance-based
            chance = effect.get_fitting_usage_chance(self)
            if chance is None:
                continue
            side_effect_chances[effect_id] = chance
        return side_effect_chances

    # Item-specific properties
    @property
    def slot(self):
        """Return slot this booster takes."""
        return self._type_attrs.get(AttrId.boosterness)

    # Attribute calculation-related properties
    _modifier_domain = ModDomain.character
    _owner_modifiable = False
    _solsys_carrier = None

    # Auxiliary methods
    def __repr__(self):
        spec = [['type_id', '_type_id']]
        return make_repr_str(self, spec)
