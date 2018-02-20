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
from eos.eve_object.effect.dmg_dealer.base import DmgDealerEffect
from eos.eve_object.effect.fighter_effect import FighterEffect
from eos.fit.stats_container import DmgStats


class FighterAbilityKamikaze(DmgDealerEffect, FighterEffect):

    def get_volley(self, item):
        if not self.get_cycles_until_reload(item):
            return DmgStats(0, 0, 0, 0)
        em = item.attrs.get(AttrId.fighter_ability_kamikaze_dmg_em, 0)
        therm = item.attrs.get(AttrId.fighter_ability_kamikaze_dmg_therm, 0)
        kin = item.attrs.get(AttrId.fighter_ability_kamikaze_dmg_kin, 0)
        expl = item.attrs.get(AttrId.fighter_ability_kamikaze_dmg_expl, 0)
        squad_size = self.get_squad_size(item)
        return DmgStats(em, therm, kin, expl, squad_size)

    def get_dps(self, item, reload):
        return DmgStats(0, 0, 0, 0)

    def get_applied_volley(self, item, tgt_data):
        raise NotImplementedError

    def get_applied_dps(self, item, tgt_data, reload):
        return DmgStats(0, 0, 0, 0)

    def get_cycles_until_reload(self, item):
        return 1
