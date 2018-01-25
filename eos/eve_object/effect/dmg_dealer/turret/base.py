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
from eos.fit.stats_container import DmgStats
from ..base import DmgDealerEffect


class TurretDmgEffect(DmgDealerEffect, metaclass=ABCMeta):

    @abstractmethod
    def _get_base_dmg_item(self, item):
        """Get item which carries base damage attributes."""
        ...

    def get_volley(self, item):
        if self.get_cycles_until_reload(item) is None:
            return DmgStats(0, 0, 0, 0)
        base_dmg_item = self._get_base_dmg_item(item)
        if base_dmg_item is None:
            return DmgStats(0, 0, 0, 0)
        em = base_dmg_item.attrs.get(AttrId.em_dmg, 0)
        thermal = base_dmg_item.attrs.get(AttrId.thermal_dmg, 0)
        kinetic = base_dmg_item.attrs.get(AttrId.kinetic_dmg, 0)
        explosive = base_dmg_item.attrs.get(AttrId.explosive_dmg, 0)
        multiplier = item.attrs.get(AttrId.dmg_multiplier)
        return DmgStats(em, thermal, kinetic, explosive, multiplier)

    def get_applied_volley(self, item, tgt_data):
        raise NotImplementedError
