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
from eos.eve_obj.effect import EffectFactory
from eos.eve_obj.effect.helper_func import get_cycles_until_reload_generic
from eos.stats_container import DmgStats
from .base import DmgDealerEffect


class UseMissiles(DmgDealerEffect):

    def get_cycles_until_reload(self, item):
        return get_cycles_until_reload_generic(item)

    def get_volley(self, item):
        if not self.get_cycles_until_reload(item):
            return DmgStats(0, 0, 0, 0)
        # If module can cycle until reload, it means we can assume that there's
        # a charge loaded
        charge = self.get_charge(item)
        charge_defeff_id = charge._type_default_effect_id
        if (
            charge_defeff_id is None or
            charge_defeff_id not in charge._running_effect_ids or
            charge_defeff_id not in (
                EffectId.missile_launching,
                EffectId.fof_missile_launching,
                EffectId.bomb_launching)
        ):
            return DmgStats(0, 0, 0, 0)
        em = charge.attrs.get(AttrId.em_dmg, 0)
        therm = charge.attrs.get(AttrId.therm_dmg, 0)
        kin = charge.attrs.get(AttrId.kin_dmg, 0)
        expl = charge.attrs.get(AttrId.expl_dmg, 0)
        return DmgStats(em, therm, kin, expl)

    def get_applied_volley(self, item, tgt_data):
        raise NotImplementedError


EffectFactory.reg_cust_class_by_id(UseMissiles, EffectId.use_missiles)
