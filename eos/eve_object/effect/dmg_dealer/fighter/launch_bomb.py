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
from eos.eve_object.effect.dmg_dealer.base import DmgDealerEffect
from eos.eve_object.effect.fighter_effect import FighterEffect
from eos.fit.stats_container import DmgStats


class FighterAbilityLaunchBomb(DmgDealerEffect, FighterEffect):

    def get_volley(self, item):
        if not self.get_cycles_until_reload(item):
            return DmgStats(0, 0, 0, 0)
        charge = self.get_charge(item)
        if charge is None:
            return DmgStats(0, 0, 0, 0)
        charge_defeff_id = charge._type_default_effect_id
        if (
            charge_defeff_id != EffectId.bomb_launching or
            charge_defeff_id not in charge._running_effect_ids
        ):
            return DmgStats(0, 0, 0, 0)
        em = charge.attrs.get(AttrId.em_dmg, 0)
        therm = charge.attrs.get(AttrId.therm_dmg, 0)
        kin = charge.attrs.get(AttrId.kin_dmg, 0)
        expl = charge.attrs.get(AttrId.expl_dmg, 0)
        squad_size = self.get_squad_size(item)
        return DmgStats(em, therm, kin, expl, squad_size)

    def get_applied_volley(self, item, tgt_data):
        raise NotImplementedError

    def get_autocharge_type_id(self, item):
        try:
            ammo_type_id = (
                item._type_attrs[AttrId.fighter_ability_launch_bomb_type])
        except KeyError:
            return None
        return int(ammo_type_id)
