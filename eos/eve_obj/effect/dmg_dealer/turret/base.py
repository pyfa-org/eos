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


from abc import ABCMeta
from abc import abstractmethod

from eos.const.eve import AttrId
from eos.eve_obj.effect.dmg_dealer.base import DmgDealerEffect
from eos.stats_container import DmgStats


class TurretDmgEffect(DmgDealerEffect, metaclass=ABCMeta):

    @abstractmethod
    def _get_base_dmg_item(self, item):
        """Get item which carries base damage attributes."""
        ...

    def get_volley(self, item):
        if not self.get_cycles_until_reload(item):
            return DmgStats(0, 0, 0, 0)
        base_dmg_item = self._get_base_dmg_item(item)
        if base_dmg_item is None:
            return DmgStats(0, 0, 0, 0)
        em = base_dmg_item.attrs.get(AttrId.em_dmg, 0)
        therm = base_dmg_item.attrs.get(AttrId.therm_dmg, 0)
        kin = base_dmg_item.attrs.get(AttrId.kin_dmg, 0)
        expl = base_dmg_item.attrs.get(AttrId.expl_dmg, 0)
        mult = item.attrs.get(AttrId.dmg_mult)
        return DmgStats(em, therm, kin, expl, mult)

    def get_applied_volley(self, item, tgt_data):
        raise NotImplementedError
