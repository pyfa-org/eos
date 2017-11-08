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


from eos.fit.item.mixin.damage_dealer import (
    DamageDealerMixin, BASIC_MAP, CHARGE_MAP)
from eos.fit.helper import DamageTypesTotal
from eos.fit.pubsub.message import EffectsStarted, EffectsStopped
from eos.util.keyed_storage import KeyedStorage
from .base import BaseStatRegister


PRIMARY_DAMAGE_EFFECTS = set(BASIC_MAP).union(CHARGE_MAP)


class DamageDealerRegister(BaseStatRegister):
    """Class which tracks all items which can potentially deal damage.

    Using this data, it provides functionality to fetch various aggregated
    stats.
    """

    def __init__(self, msg_broker):
        # Format: {item: {damage dealing effect IDs}}
        self.__dealers = KeyedStorage()
        msg_broker._subscribe(self, self._handler_map.keys())

    def _handle_effects_started(self, message):
        if not isinstance(message.item, DamageDealerMixin):
            return
        damage_effects = message.effect_ids.intersection(PRIMARY_DAMAGE_EFFECTS)
        if damage_effects:
            self.__dealers.add_data_set(message.item, damage_effects)

    def _handle_effects_stopped(self, message):
        if not isinstance(message.item, DamageDealerMixin):
            return
        damage_effects = message.effect_ids.intersection(PRIMARY_DAMAGE_EFFECTS)
        if damage_effects:
            self.__dealers.rm_data_set(message.item, damage_effects)

    _handler_map = {
        EffectsStarted: _handle_effects_started,
        EffectsStopped: _handle_effects_stopped}

    def _collect_damage_stats(self, item_filter, method_name, *args, **kwargs):
        """Fetch stats from all registered items.

        Args:
            item_filter: When iterating over fit items, this function is called.
                If evaluated as True, this item is taken into consideration,
                else not. If argument is None, all items 'pass filter'.
            method_name, *args, **kwargs: Method name, which will be called for
                each item to request its damage stats. Args and kwargs are
                arguments which are passed to this method.

        Return value: Returns: DamageTypesTotal helper container instance.
        """
        em, therm, kin, expl = None, None, None, None
        for item in self.__dealers:
            if item_filter is not None and not item_filter(item):
                continue
            stat = getattr(item, method_name)(*args, **kwargs)
            # Guards against both aggregated values equal to None and item
            # values equal to None. If aggregated value is None, assigns value
            # from item stats to aggregated. If item stat is None, just ignores
            # it.
            try:
                em += stat.em
            except TypeError:
                if em is None:
                    em = stat.em
            try:
                therm += stat.thermal
            except TypeError:
                if therm is None:
                    therm = stat.thermal
            try:
                kin += stat.kinetic
            except TypeError:
                if kin is None:
                    kin = stat.kinetic
            try:
                expl += stat.explosive
            except TypeError:
                if expl is None:
                    expl = stat.explosive
        return DamageTypesTotal(
            em=em, thermal=therm, kinetic=kin, explosive=expl)
