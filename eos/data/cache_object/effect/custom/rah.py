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


from logging import getLogger

from eos.const.eos import EffectBuildStatus, State, ModifierTargetFilter, ModifierDomain, ModifierOperator
from eos.const.eve import Attribute
from eos.data.cache_object import DogmaModifier


logger = getLogger(__name__)


def add_rah_modifiers(effect):
    if len(effect.modifiers) > 0:
        msg = 'reactive armor hardener effect has modifiers, overwriting them'
        logger.info(msg)
    em_modifier = DogmaModifier(
        tgt_filter=ModifierTargetFilter.item,
        tgt_domain=ModifierDomain.ship,
        state=State.active,
        src_attr=Attribute.armor_em_damage_resonance,
        operator=ModifierOperator.pre_mul,
        tgt_attr=Attribute.armor_em_damage_resonance
    )
    thermal_modifier = DogmaModifier(
        tgt_filter=ModifierTargetFilter.item,
        tgt_domain=ModifierDomain.ship,
        state=State.active,
        src_attr=Attribute.armor_thermal_damage_resonance,
        operator=ModifierOperator.pre_mul,
        tgt_attr=Attribute.armor_thermal_damage_resonance
    )
    kinetic_modifier = DogmaModifier(
        tgt_filter=ModifierTargetFilter.item,
        tgt_domain=ModifierDomain.ship,
        state=State.active,
        src_attr=Attribute.armor_kinetic_damage_resonance,
        operator=ModifierOperator.pre_mul,
        tgt_attr=Attribute.armor_kinetic_damage_resonance
    )
    explosive_modifier = DogmaModifier(
        tgt_filter=ModifierTargetFilter.item,
        tgt_domain=ModifierDomain.ship,
        state=State.active,
        src_attr=Attribute.armor_explosive_damage_resonance,
        operator=ModifierOperator.pre_mul,
        tgt_attr=Attribute.armor_explosive_damage_resonance
    )
    effect.modifiers = (em_modifier, thermal_modifier, kinetic_modifier, explosive_modifier)
    effect.build_status = EffectBuildStatus.custom