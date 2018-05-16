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


from logging import getLogger

from eos.const.eos import EffectBuildStatus
from eos.const.eve import EffectId
from eos.eve_obj.effect import EffectFactory
from .modifier import make_rah_modifiers


logger = getLogger(__name__)


def add_rah_modifiers(effect):
    if effect.modifiers:
        msg = 'reactive armor hardener effect has modifiers, overwriting them'
        logger.warning(msg)
    effect.modifiers = make_rah_modifiers()
    effect.build_status = EffectBuildStatus.custom


EffectFactory.reg_cust_instance_by_id(
    add_rah_modifiers,
    EffectId.adaptive_armor_hardener)
