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
from .base import TurretDmgEffect


class ProjectileFired(TurretDmgEffect):

    id = EffectId.projectile_fired

    def _get_base_dmg_item(self, item):
        return self.get_charge(item)

    def get_cycles_until_reload(self, item):
        charge_quantity = item.charge_quantity
        charge_rate = item.attrs.get(AttrId.charge_rate)
        if not charge_rate or charge_quantity is None:
            return None
        cycles = charge_quantity // int(charge_rate)
        return cycles
