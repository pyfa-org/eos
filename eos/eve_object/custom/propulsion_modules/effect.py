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

from eos.const.eos import (
    EffectBuildStatus, ModDomain, ModOperator, ModTgtFilter)
from eos.const.eve import AttrId
from .modifier import PropulsionModuleVelocityBoostModifier
from ...modifier import DogmaModifier


logger = getLogger(__name__)


def add_ab_modifiers(effect):
    if effect.modifiers:
        msg = 'afterburner effect has modifiers, overwriting them'
        logger.info(msg)
    mass_modifier = DogmaModifier(
        tgt_filter=ModTgtFilter.item,
        tgt_domain=ModDomain.ship,
        tgt_attr_id=AttrId.mass,
        operator=ModOperator.mod_add,
        src_attr_id=AttrId.mass_addition)
    velocity_modifier = PropulsionModuleVelocityBoostModifier()
    effect.modifiers = (mass_modifier, velocity_modifier)
    effect.build_status = EffectBuildStatus.custom


def add_mwd_modifiers(effect):
    if effect.modifiers:
        msg = 'microwarpdrive effect has modifiers, overwriting them'
        logger.info(msg)
    mass_modifier = DogmaModifier(
        tgt_filter=ModTgtFilter.item,
        tgt_domain=ModDomain.ship,
        tgt_attr_id=AttrId.mass,
        operator=ModOperator.mod_add,
        src_attr_id=AttrId.mass_addition)
    signature_modifier = DogmaModifier(
        tgt_filter=ModTgtFilter.item,
        tgt_domain=ModDomain.ship,
        tgt_attr_id=AttrId.signature_radius,
        operator=ModOperator.post_percent,
        src_attr_id=AttrId.signature_radius_bonus)
    velocity_modifier = PropulsionModuleVelocityBoostModifier()
    effect.modifiers = (mass_modifier, signature_modifier, velocity_modifier)
    effect.build_status = EffectBuildStatus.custom
