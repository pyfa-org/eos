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
    EffectBuildStatus, EosEffectId, ModDomain, ModOperator, ModTgtFilter)
from eos.const.eve import AttrId, EffectCategoryId, TypeId
from eos.eve_object import DogmaModifier, EffectFactory


def add_char_missile_dmg_multiplier(item_type):
    """Apply message damage multiplier to missiles.

    Some modules, like ballistic control systems, do not affect missile
    attributes directly; instead, they affect an attribute on the character,
    which, in turn, should affect missiles. The problem is that it doesn't
    affect missiles (probably some hardcoding on CCP's part), so we're adding it
    manually.
    """
    modifiers = []
    for dmg_attr_id in (
        AttrId.em_dmg,
        AttrId.thermal_dmg,
        AttrId.kinetic_dmg,
        AttrId.explosive_dmg
    ):
        modifiers.append(DogmaModifier(
            tgt_filter=ModTgtFilter.owner_skillrq,
            tgt_domain=ModDomain.character,
            tgt_filter_extra_arg=TypeId.missile_launcher_operation,
            tgt_attr_id=dmg_attr_id,
            operator=ModOperator.pre_mul,
            src_attr_id=AttrId.missile_dmg_multiplier))
    effect = EffectFactory.make(
        effect_id=EosEffectId.char_missile_dmg,
        category_id=EffectCategoryId.passive,
        is_offensive=False,
        is_assistance=False,
        build_status=EffectBuildStatus.custom,
        modifiers=tuple(modifiers))
    item_type.effects[effect.id] = effect
