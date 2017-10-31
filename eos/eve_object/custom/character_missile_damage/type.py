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


from eos.const.eos import (
    EffectBuildStatus, EosEffectId, ModifierDomain, ModifierOperator,
    ModifierTargetFilter)
from eos.const.eve import AttributeId, EffectCategoryId, TypeId
from ...effect import Effect
from ...modifier import DogmaModifier


def add_character_missile_damage_multiplier(eve_type):
    """Apply message damage multiplier to missiles.

    Some modules, like ballistic control systems, do not affect missile
    attributes directly; instead, they affect an attribute on the character,
    which, in turn, should affect missiles. The problem is that it doesn't
    affect missiles (probably some hardcoding on CCP's part), so we're adding it
    manually.
    """
    modifiers = []
    for damage_attr_id in (
        AttributeId.em_damage,
        AttributeId.thermal_damage,
        AttributeId.kinetic_damage,
        AttributeId.explosive_damage
    ):
        modifiers.append(DogmaModifier(
            tgt_filter=ModifierTargetFilter.owner_skillrq,
            tgt_domain=ModifierDomain.character,
            tgt_filter_extra_arg=TypeId.missile_launcher_operation,
            tgt_attr_id=damage_attr_id,
            operator=ModifierOperator.pre_mul,
            src_attr_id=AttributeId.missile_damage_multiplier))
    effect = Effect(
        effect_id=EosEffectId.char_missile_dmg,
        category_id=EffectCategoryId.passive,
        is_offensive=False,
        is_assistance=False,
        build_status=EffectBuildStatus.custom,
        modifiers=tuple(modifiers))
    eve_type.effects[effect.id] = effect
