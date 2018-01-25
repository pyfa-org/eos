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


class FighterAbilityAttackM(DmgDealerEffect):

    def get_volley(self, item):
        em = item.attrs.get(
            AttrId.fighter_ability_attack_missile_dmg_em, 0)
        thermal = item.attrs.get(
            AttrId.fighter_ability_attack_missile_dmg_thermal, 0)
        kinetic = item.attrs.get(
            AttrId.fighter_ability_attack_missile_dmg_kinetic, 0)
        explosive = item.attrs.get(
            AttrId.fighter_ability_attack_missile_dmg_explosive, 0)
        dmg_multiplier = item.attrs.get(
            AttrId.fighter_ability_attack_missile_dmg_multiplier, 1)
        try:
            squad_size = item.squad_size
        except AttributeError:
            squad_size = 1
        multiplier = dmg_multiplier * squad_size
        return DmgStats(em, thermal, kinetic, explosive, multiplier)

    def get_applied_volley(self, item, tgt_data):
        raise NotImplementedError
