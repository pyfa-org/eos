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


from eos.const.eve import AttrId
from eos.const.eve import EffectId
from eos.eve_object.effect import EffectFactory
from .base import DmgDealerEffect


class TgtAttack(DmgDealerEffect):

    def get_volley(self, item, tgt_resists):
        return

    def get_dps(self, item, tgt_resists, reload):
        return

    def get_applied_volley(self, item, tgt_data, tgt_resists):
        return

    def get_applied_dps(self, item, tgt_data, tgt_resists, reload):
        return

    def get_autocharge_type_id(self, item):
        try:
            ammo_type_id = item.attrs[AttrId.ammo_loaded]
        except KeyError:
            return None
        return int(ammo_type_id)


EffectFactory.reg_cust_class_by_id(TgtAttack, EffectId.tgt_attack)
