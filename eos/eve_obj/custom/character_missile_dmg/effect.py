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


from eos.const.eos import EffectBuildStatus
from eos.const.eos import EosEffectId
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from eos.const.eve import TypeId
from eos.eve_obj.effect import EffectFactory
from eos.eve_obj.modifier import DogmaModifier


def make_missile_dmg_effect():
    modifiers = []
    for dmg_attr_id in (
        AttrId.em_dmg,
        AttrId.therm_dmg,
        AttrId.kin_dmg,
        AttrId.expl_dmg
    ):
        modifiers.append(DogmaModifier(
            tgt_filter=ModTgtFilter.owner_skillrq,
            tgt_domain=ModDomain.character,
            tgt_filter_extra_arg=TypeId.missile_launcher_operation,
            tgt_attr_id=dmg_attr_id,
            operator=ModOperator.post_mul_immune,
            src_attr_id=AttrId.missile_dmg_mult))
    missile_dmg_effect = EffectFactory.make(
        effect_id=EosEffectId.char_missile_dmg,
        category_id=EffectCategoryId.passive,
        is_offensive=False,
        is_assistance=False,
        build_status=EffectBuildStatus.custom,
        modifiers=tuple(modifiers))
    return missile_dmg_effect
