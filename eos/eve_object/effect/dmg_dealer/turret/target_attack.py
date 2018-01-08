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


from math import inf

from eos.const.eve import AttrId
from eos.const.eve import EffectId
from eos.util.float import float_to_int
from .base import TurretDmgEffect


class TargetAttack(TurretDmgEffect):

    id = EffectId.target_attack

    def _get_base_dmg_item(self, item):
        charge = self.get_charge(item)
        dmg_attr_ids = {
            AttrId.em_dmg,
            AttrId.thermal_dmg,
            AttrId.kinetic_dmg,
            AttrId.explosive_dmg}
        if charge is not None and dmg_attr_ids.intersection(charge._type_attrs):
            return charge
        elif dmg_attr_ids.intersection(item._type_attrs):
            return item
        else:
            return None

    def get_autocharge_type_id(self, item):
        try:
            ammo_type_id = item._type_attrs[AttrId.ammo_loaded]
        except KeyError:
            return None
        return int(ammo_type_id)

    def get_cycles_until_reload(self, item):
        base_dmg_item = self._get_base_dmg_item(item)
        try:
            charge = item.charge
        except AttributeError:
            charge = None
        # If item which contains base damage stats is not item's regular charge,
        # it means that either autocharge or item itself provides base damage
        # stats. In either case, effect can be cycled infinitely
        if base_dmg_item is not charge:
            return inf
        # If charge should carry damage stats but charge is not there, effect
        # cannot cycle
        if charge is None:
            return 0
        # Non-damageable crystals can cycle infinitely
        if not charge.attrs.get(AttrId.crystals_get_damaged):
            return inf
        # Damageable crystals must have all damage-related stats to calculate
        # how many times they can cycle
        try:
            hp = charge.attrs[AttrId.hp]
            chance = charge.attrs[AttrId.crystal_volatility_chance]
            dmg = charge.attrs[AttrId.crystal_volatility_dmg]
        except KeyError:
            return 0
        charge_quantity = item.charge_quantity
        # If item cannot fit any charges, effect cannot cycle
        if not charge_quantity:
            return 0
        cycles = float_to_int(hp / dmg / chance) * charge_quantity
        return cycles
