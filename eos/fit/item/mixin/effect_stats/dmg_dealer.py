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


from eos.eve_object.effect.dmg_dealer.base import DmgDealerEffect
from ..base import BaseItemMixin


class DmgDealerMixin(BaseItemMixin):
    """Expose damage dealing effect stats to item."""

    def __dd_effect_iter(self):
        for effect in self._type_effects:
            if not isinstance(effect, DmgDealerEffect):
                continue
            if effect.id not in self._running_effect_ids:
                continue
            yield effect

    def get_nominal_volley(self, tgt_resists=None):
        pass

    def get_nominal_dps(self, tgt_resists=None, reload=False):
        pass

    def get_volley_vs_tgt(self, tgt_data=None, tgt_resists=None):
        # TODO
        pass

    def get_chance_to_hit(self, tgt_data=None):
        # TODO
        pass

    def get_dps_vs_tgt(self, tgt_data=None, tgt_resists=None, reload=True):
        # TODO
        pass
