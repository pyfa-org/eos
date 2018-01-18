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
from eos.eve_object.effect.helper_func import get_cycles_until_reload_generic
from eos.fit.stats_container import DmgTypesTotal
from .base import DmgDealerEffect


class UseMissiles(DmgDealerEffect):

    def get_cycles_until_reload(self, item):
        return get_cycles_until_reload_generic(item)

    def get_volley(self, item):
        if self.get_cycles_until_reload(item) is None:
            return DmgTypesTotal(None, None, None, None)
        # If module can cycle until reload, it means we can assume that there's
        # a charge loaded
        charge = self.get_charge(item)
        charge_defeff_id = charge._type_default_effect_id
        if (
            charge_defeff_id is None or
            charge_defeff_id not in charge._running_effect_ids or
            charge_defeff_id not in (
                EffectId.missile_launching,
                EffectId.bomb_launching)
        ):
            return DmgTypesTotal(None, None, None, None)
        em = charge.attrs.get(AttrId.em_dmg)
        thermal = charge.attrs.get(AttrId.thermal_dmg)
        kinetic = charge.attrs.get(AttrId.kinetic_dmg)
        explosive = charge.attrs.get(AttrId.explosive_dmg)
        return DmgTypesTotal(em, thermal, kinetic, explosive)

    def get_applied_volley(self, item, tgt_data):
        raise NotImplementedError


EffectFactory.reg_cust_class_by_id(UseMissiles, EffectId.use_missiles)
