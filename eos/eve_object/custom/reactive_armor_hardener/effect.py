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
from ...modifier import DogmaModifier


logger = getLogger(__name__)


def add_rah_modifiers(effect):
    if effect.modifiers:
        msg = 'reactive armor hardener effect has modifiers, overwriting them'
        logger.warning(msg)
    effect.modifiers = tuple(
        DogmaModifier(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=attr_id,
            operator=ModOperator.pre_mul,
            src_attr_id=attr_id)
        for attr_id in (
            AttrId.armor_em_dmg_resonance,
            AttrId.armor_thermal_dmg_resonance,
            AttrId.armor_kinetic_dmg_resonance,
            AttrId.armor_explosive_dmg_resonance))
    effect.build_status = EffectBuildStatus.custom
