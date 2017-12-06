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


"""
In CCP dogma code, 'online' effect has custom processing. Actual effect has
'active' effect category, which lets all item types with it to be in active
state according to eos' effect handling. We do not want any special processing,
thus just fix it here.
"""


from logging import getLogger

from eos.const.eve import EffectCategoryId
from eos.const.eve import EffectId
from eos.eve_object import EffectFactory


logger = getLogger(__name__)


def fix_online_category(effect):
    if effect.category_id == EffectCategoryId.online:
        msg = 'online effect category does not need to be adjusted'
        logger.info(msg)
    else:
        effect.category_id = EffectCategoryId.online


EffectFactory.reg_cust_instance_by_id(fix_online_category, EffectId.online)
