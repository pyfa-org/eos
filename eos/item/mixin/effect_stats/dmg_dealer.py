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


from eos.eve_obj.effect.dmg_dealer.base import DmgDealerEffect
from eos.item.mixin.base import BaseItemMixin
from eos.stats_container import DmgStats


class DmgDealerMixin(BaseItemMixin):
    """Expose damage dealing effect stats to item."""

    def __dd_effect_iter(self):
        effects = []
        suppressor_effects = []
        for effect in self._type_effects.values():
            if not isinstance(effect, DmgDealerEffect):
                continue
            if effect.id not in self._running_effect_ids:
                continue
            effects.append(effect)
            if effect.suppress_dds:
                suppressor_effects.append(effect)
        # If we have any effects which suppress other effects on this item,
        # we're going to cycle only through them
        if suppressor_effects:
            effects = suppressor_effects
        for effect in effects:
            yield effect

    def get_volley(self, tgt_resists=None):
        volleys = []
        for effect in self.__dd_effect_iter():
            volley = effect.get_volley(self)
            volleys.append(volley)
        return DmgStats._combine(volleys, tgt_resists)

    def get_dps(self, reload=False, tgt_resists=None):
        dpss = []
        for effect in self.__dd_effect_iter():
            dps = effect.get_dps(self, reload)
            dpss.append(dps)
        return DmgStats._combine(dpss, tgt_resists)

    def get_applied_volley(self, tgt_data=None, tgt_resists=None):
        raise NotImplementedError

    def get_applied_dps(self, reload=False, tgt_data=None, tgt_resists=None):
        raise NotImplementedError
