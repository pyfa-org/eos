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


from eos.eve_obj.effect.repairs.base import RemoteArmorRepairEffect
from eos.eve_obj.effect.repairs.base import RemoteShieldRepairEffect
from eos.item.mixin.base import BaseItemMixin


class RemoteRepairMixin(BaseItemMixin):

    def __repair_effect_iter(self, effect_class):
        for effect in self._type_effects.values():
            if not isinstance(effect, effect_class):
                continue
            if effect.id not in self._running_effect_ids:
                continue
            yield effect

    def get_armor_rps(self, reload=False):
        rps = 0
        for effect in self.__repair_effect_iter(RemoteArmorRepairEffect):
            rps += effect.get_rps(self, reload=reload)
        return rps

    def get_shield_rps(self, reload=False):
        rps = 0
        for effect in self.__repair_effect_iter(RemoteShieldRepairEffect):
            rps += effect.get_rps(self, reload=reload)
        return rps
