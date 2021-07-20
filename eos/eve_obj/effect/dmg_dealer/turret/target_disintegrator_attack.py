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
from eos.eve_obj.effect.helper_func import get_cycles_until_reload_generic
from eos.stats_container import DmgStats
from .base import TurretDmgEffect


class TargetDisintegratorAttack(TurretDmgEffect):

    def _get_base_dmg_item(self, item):
        return self.get_charge(item)

    def get_volley(self, item):
        volley = TurretDmgEffect.get_volley(self, item)
        try:
            spoolup_mult = item.attrs[AttrId.dmg_mult_bonus_max]
        except KeyError:
            return volley
        return DmgStats(
            volley.em,
            volley.thermal,
            volley.kinetic,
            volley.explosive,
            1 + spoolup_mult)

    def get_cycles_until_reload(self, item):
        return get_cycles_until_reload_generic(item)
