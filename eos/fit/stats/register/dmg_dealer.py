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
from eos.fit.message import EffectsStarted
from eos.fit.message import EffectsStopped
from eos.fit.stats_container import DmgStats
from eos.util.keyed_storage import KeyedStorage
from .base import BaseStatRegister


class DmgDealerRegister(BaseStatRegister):
    """Class which tracks all effects which deal damage.

    Provides functionality to fetch various aggregated stats.
    """

    def __init__(self, fit):
        # Format: {(item, effect), ...}
        self.__dmg_dealers = KeyedStorage()
        fit._subscribe(self, self._handler_map.keys())

    def get_volley(self, item_filter, tgt_resists):
        volleys = []
        for item in self.__dd_iter(item_filter):
            volley = item.get_volley(tgt_resists)
            volleys.append(volley)
        return DmgStats._combine(volleys)

    def get_dps(self, item_filter, reload, tgt_resists):
        dpss = []
        for item in self.__dd_iter(item_filter):
            dps = item.get_dps(reload, tgt_resists)
            dpss.append(dps)
        return DmgStats._combine(dpss)

    def __dd_iter(self, item_filter):
        for item in self.__dmg_dealers:
            if item_filter is None or item_filter(item):
                yield item

    # Message handling
    def _handle_effects_started(self, msg):
        item_effects = msg.item._type_effects
        for effect_id in msg.effect_ids:
            effect = item_effects[effect_id]
            if isinstance(effect, DmgDealerEffect):
                self.__dmg_dealers.add_data_entry(msg.item, effect)

    def _handle_effects_stopped(self, msg):
        item_effects = msg.item._type_effects
        for effect_id in msg.effect_ids:
            effect = item_effects[effect_id]
            if isinstance(effect, DmgDealerEffect):
                self.__dmg_dealers.rm_data_entry(msg.item, effect)

    _handler_map = {
        EffectsStarted: _handle_effects_started,
        EffectsStopped: _handle_effects_stopped}
