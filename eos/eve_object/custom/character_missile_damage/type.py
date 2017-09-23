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


from eos.const.eos import EffectBuildStatus, EosEffect, ModifierDomain, ModifierOperator, ModifierTargetFilter
from eos.const.eve import Attribute, Type, EffectCategory
from ...effect import Effect
from ...modifier import DogmaModifier


def add_character_missile_damage_multiplier(eve_type):
    """
    Some modules, like ballistic control systems, do not affect
    missile attributes directly; instead, they affect an attribute
    on the character, which, in turn, should affect missiles. The
    problem is that it doesn't affect missiles (probably some
    hardcoding on CCP's part), so we're adding it manually.
    """
    modifiers = []
    for damage_attr in (
        Attribute.em_damage, Attribute.thermal_damage,
        Attribute.kinetic_damage, Attribute.explosive_damage
    ):
        modifiers.append(DogmaModifier(
            tgt_filter=ModifierTargetFilter.owner_skillrq, tgt_domain=ModifierDomain.character,
            tgt_filter_extra_arg=Type.missile_launcher_operation, tgt_attr=damage_attr,
            operator=ModifierOperator.pre_mul, src_attr=Attribute.missile_damage_multiplier
        ))
    effect = Effect(
        effect_id=EosEffect.char_missile_dmg,
        category=EffectCategory.passive,
        is_offensive=False,
        is_assistance=False,
        build_status=EffectBuildStatus.custom,
        modifiers=tuple(modifiers)
    )
    eve_type.effects[effect.id] = effect
