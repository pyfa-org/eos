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


from eos.const.eos import EffectMode
from eos.const.eos import State
from eos.const.eve import AttrId
from eos.const.eve import fighter_ability_map
from eos.fit.misc.effect_status import EffectStatusResolver
from eos.util.repr import make_repr_str
from .mixin.effect_stats import EffectStatsMixin
from .mixin.state import MutableStateMixin
from .mixin.tanking import BufferTankingMixin


ABILITY_EFFECT_STATE = State.active


class FighterSquad(MutableStateMixin, BufferTankingMixin, EffectStatsMixin):
    """Represents a fighter squad.

    Unlike drones, fighter squad is single entity.

    Args:
        type_id: Identifier of item type which should serve as base for this
            fighter squad.
        state (optional): Initial state fighter squad takes, default is offline
            (squad is in fighter tube).
    """

    def __init__(self, type_id, state=State.offline):
        super().__init__(type_id=type_id, state=state)

    # Ability-related methods
    @property
    def abilities(self):
        abilities = {}
        for ability_id in self.__ability_ids:
            effect_id = fighter_ability_map[ability_id]
            try:
                effect = self._type_effects[effect_id]
            except KeyError:
                continue
            if effect._state != ABILITY_EFFECT_STATE:
                continue
            ability_status = EffectStatusResolver.resolve_effect_status(
                self, effect_id, state_override=ABILITY_EFFECT_STATE)
            abilities[ability_id] = ability_status
        return abilities

    def set_ability_status(self, ability_id, status):
        if ability_id not in self.__ability_ids:
            return
        effect_id = fighter_ability_map[ability_id]
        default_effect_id = self._type_default_effect_id
        # Default effects are running by default if item is in active+ state,
        # thus they have special processing
        if effect_id == default_effect_id:
            if status:
                effect_mode = EffectMode.full_compliance
            else:
                effect_mode = EffectMode.force_stop
        # Non-default effects
        else:
            if status:
                effect_mode = EffectMode.state_compliance
            else:
                effect_mode = EffectMode.full_compliance
        self.set_effect_mode(effect_id, effect_mode)

    @property
    def __ability_ids(self):
        try:
            return self._type.ability_ids
        except AttributeError:
            return ()

    # Item-specific properties
    @property
    def squad_size(self):
        return self.attrs.get(AttrId.fighter_squadron_max_size)

    # Attribute calculation-related properties
    _modifier_domain = None
    _owner_modifiable = True

    # Auxiliary methods
    def __repr__(self):
        spec = [['type_id', '_type_id'], 'state']
        return make_repr_str(self, spec)
