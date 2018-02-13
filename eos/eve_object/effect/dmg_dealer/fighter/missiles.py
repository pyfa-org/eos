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
from eos.fit.stats_container import DmgStats
from ..base import DmgDealerEffect


class FighterAbilityMissiles(DmgDealerEffect):

    def get_volley(self, item):
        em = item.attrs.get(AttrId.fighter_ability_missiles_dmg_em, 0)
        therm = item.attrs.get(AttrId.fighter_ability_missiles_dmg_therm, 0)
        kin = item.attrs.get(AttrId.fighter_ability_missiles_dmg_kin, 0)
        expl = item.attrs.get(AttrId.fighter_ability_missiles_dmg_expl, 0)
        dmg_mult = item.attrs.get(AttrId.fighter_ability_missiles_dmg_mult, 1)
        try:
            squad_size = item.squad_size
        except AttributeError:
            squad_size = 1
        mult = dmg_mult * squad_size
        return DmgStats(em, therm, kin, expl, mult)

    def get_applied_volley(self, item, tgt_data):
        raise NotImplementedError

    def get_cycles_until_reload(self, item):
        return item._type.effects_data[self.id].charge_quantity

    def get_forced_inactive_time(self, item):
        cooldown_time = item._type.effects_data[self.id].cooldown_time
        cycle_time = self.get_duration(item)
        return max(cooldown_time - cycle_time, 0)
