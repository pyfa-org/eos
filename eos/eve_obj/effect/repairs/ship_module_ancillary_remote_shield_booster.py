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


from eos.const.eve import AttrId
from eos.const.eve import EffectId
from eos.eve_obj.effect import EffectFactory
from .base import RemoteShieldRepairEffect


class ShipModuleAncillaryRemoteShieldBooster(RemoteShieldRepairEffect):

    def get_rep_amount(self, item):
        return item.attrs.get(AttrId.shield_bonus, 0)


EffectFactory.register_class_by_id(
    ShipModuleAncillaryRemoteShieldBooster,
    EffectId.ship_module_ancillary_remote_shield_booster)
