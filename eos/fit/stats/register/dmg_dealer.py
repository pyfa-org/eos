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
from eos.fit.stats_container import DmgTypesTotal
from .base import BaseStatRegister


class DmgDealerRegister(BaseStatRegister):
    """Class which tracks all effects which deal damage.

    Provides functionality to fetch various aggregated stats.
    """

    def __init__(self, msg_broker):
        # Format: {(item, effect), ...}
        self.__dealers = set()
        msg_broker._subscribe(self, self._handler_map.keys())

    def _handle_effects_started(self, msg):
        item_effects = msg.item._type_effects
        for effect_id in msg.effect_ids:
            effect = item_effects[effect_id]
            if isinstance(effect, DmgDealerEffect):
                self.__dealers.add((msg.item, effect))

    def _handle_effects_stopped(self, msg):
        item_effects = msg.item._type_effects
        for effect_id in msg.effect_ids:
            effect = item_effects[effect_id]
            if isinstance(effect, DmgDealerEffect):
                self.__dealers.remove((msg.item, effect))

    _handler_map = {
        EffectsStarted: _handle_effects_started,
        EffectsStopped: _handle_effects_stopped}

    def _collect_dmg_stats(self, item_filter, method_name, *args, **kwargs):
        """Fetch damage stats from all registered damage dealers.

        Args:
            item_filter: When iterating over fit items, this function is called.
                If evaluated as True, this item is taken into consideration,
                else not. If argument is None, all items 'pass filter'.
            method_name, *args, **kwargs: Method name, which will be called for
                each item to request its damage stats. Args and kwargs are
                arguments which are passed to this method.

        Returns:
            DmgTypesTotal helper container instance.
        """
        dmgs = []
        for item, effect in self.__dealers:
            if item_filter is not None and not item_filter(item):
                continue
            dmg = getattr(effect, method_name)(*args, **kwargs)
            dmgs.append(dmg)
        return DmgTypesTotal._combine(*dmgs)
