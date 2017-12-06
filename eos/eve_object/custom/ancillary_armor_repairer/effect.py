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
from eos.const.eve import EffectCategoryId
from eos.eve_object import EffectFactory
from .modifier import AncillaryRepAmountModifier

_paste_effect = None


def get_paste_effect():
    global _paste_effect
    if _paste_effect is None:
        _paste_effect = EffectFactory.make(
            effect_id=EosEffectId.ancillary_paste_armor_rep_boost,
            category_id=EffectCategoryId.passive,
            is_offensive=False,
            is_assistance=False,
            build_status=EffectBuildStatus.custom,
            modifiers=(AncillaryRepAmountModifier(),))
    return _paste_effect
