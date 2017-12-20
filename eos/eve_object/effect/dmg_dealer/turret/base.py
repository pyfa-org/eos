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
from eos.fit.stats_container import DmgTypesTotal
from ..base import DmgDealerEffect


class TurretDmgEffect(DmgDealerEffect):

    def get_volley(self, item, tgt_resists):
        charge = self.get_charge(item)
        if charge is None:
            return DmgTypesTotal(None, None, None, None)
        em = charge.attrs.get(AttrId.em_dmg)
        thermal = charge.attrs.get(AttrId.thermal_dmg)
        kinetic = charge.attrs.get(AttrId.kinetic_dmg)
        explosive = charge.attrs.get(AttrId.explosive_dmg)
        multiplier = item.attrs.get(AttrId.dmg_multiplier)
        if multiplier is not None:
            try:
                em *= multiplier
            except TypeError:
                pass
            try:
                thermal *= multiplier
            except TypeError:
                pass
            try:
                kinetic *= multiplier
            except TypeError:
                pass
            try:
                explosive *= multiplier
            except TypeError:
                pass
        return DmgTypesTotal(em, thermal, kinetic, explosive)

    def get_dps(self, item, tgt_resists, reload):
        return

    def get_applied_volley(self, item, tgt_data, tgt_resists):
        return

    def get_applied_dps(self, item, tgt_data, tgt_resists, reload):
        return
