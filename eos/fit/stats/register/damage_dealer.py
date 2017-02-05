# ===============================================================================
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
# ===============================================================================


from eos.fit.item.mixin.damage_dealer import DamageDealerMixin
from eos.fit.helpers import DamageTypesTotal
from .base import BaseStatRegister


class DamageDealerRegister(BaseStatRegister):
    """
    Class which tracks all items which can potentially
    deal damage, and provides functionality to fetch some
    useful data.
    """

    def __init__(self):
        self.__dealers = set()

    def register_item(self, item):
        if isinstance(item, DamageDealerMixin):
            self.__dealers.add(item)

    def unregister_item(self, item):
        self.__dealers.discard(item)

    def _collect_damage_stats(self, item_filter, method_name, *args, **kwargs):
        """
        Fetch stats from all registered items.

        Required arguments:
        item_filter -- function which is evaluated for each item;
        if true, item's stats are taken into consideration. Can be None.
        method_name, *args, **kwargs -- method name, which will be called
        for each item to request its damage stats. Args and kwargs are
        arguments which are passed to this method.

        Return value:
        Object with em, thermal, kinetic, explosive and total attributes
        which contain total stats for all items which satisfy passed
        conditions.
        """
        em, therm, kin, expl = None, None, None, None
        for item in self.__dealers:
            stat = getattr(item, method_name)(*args, **kwargs)
            if item_filter is not None and not item_filter(item):
                continue
            # Guards against both aggregated values equal to None and
            # item values equal to None. If aggregated value is None,
            # assigns value from item stats to aggregated. If item
            # stat is None, just ignores it.
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
        total = (em or 0) + (therm or 0) + (kin or 0) + (expl or 0)
        if total == 0 and em is None and therm is None and kin is None and expl is None:
            total = None
        return DamageTypesTotal(em=em, thermal=therm, kinetic=kin, explosive=expl, total=total)
