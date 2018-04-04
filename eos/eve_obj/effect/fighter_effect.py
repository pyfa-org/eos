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


from .effect import Effect


class FighterEffect(Effect):

    def get_cycles_until_reload(self, item):
        try:
            ability_data = item._type.effects_data[self.id]
        except KeyError:
            return None
        cycles = ability_data.charge_quantity
        if cycles == 0:
            return None
        return cycles

    def get_reload_time(self, item):
        # No fighter-related effects can be reloaded
        return None

    def get_forced_inactive_time(self, item):
        cooldown_time = item._type.effects_data[self.id].cooldown_time
        cycle_time = self.get_duration(item)
        return max(cooldown_time - cycle_time, 0)

    def get_squad_size(self, item):
        try:
            return item.squad_size
        except AttributeError:
            return 1
