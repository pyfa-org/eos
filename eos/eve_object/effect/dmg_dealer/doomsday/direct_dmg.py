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


class DoomsdayDirect(DmgDealerEffect):

    def get_volley(self, item):
        em = item.attrs.get(AttrId.em_dmg, 0)
        therm = item.attrs.get(AttrId.therm_dmg, 0)
        kin = item.attrs.get(AttrId.kin_dmg, 0)
        expl = item.attrs.get(AttrId.expl_dmg, 0)
        return DmgStats(em, therm, kin, expl)

    def get_applied_volley(self, item, tgt_data):
        raise NotImplementedError
