#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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
#===============================================================================


from eos.fit.holder.mixin.damage_dealer import DamageDealerMixin
from eos.fit.tuples import DamageTypesTotal
from .abc import StatRegister


class DamageDealerRegister(StatRegister):
    """
    Class which tracks all holders which can potentially
    deal damage, and provides functionality to fetch some
    useful data.
    """

    def __init__(self):
        self.__dealers = set()

    def register_holder(self, holder):
        if isinstance(holder, DamageDealerMixin):
            self.__dealers.add(holder)

    def unregister_holder(self, holder):
        self.__dealers.discard(holder)

    def _collect_damage_stats(self, holder_filter, method_name, *args, **kwargs):
        """
        Fetch stats from all registered holders.

        Required arguments:
        holder_filter -- function which is evaluated for each holder.
        if true, holder's stats are taken into consideration. Can be None.
        method_name, *args, **kwargs -- method name, which will be called
        for each holder to request its damage stats. Args and kwargs are
        arguments which are passed to this method.

        Return value:
        Object with em, thermal, kinetic, explosive and total attributes
        which contain total stats for all holders which satisfy passed
        conditions.
        """
        em, therm, kin, expl = 0, 0, 0, 0
        for holder in self.__dealers:
            stat = getattr(holder, method_name)(*args, **kwargs)
            if stat is None:
                continue
            if holder_filter is not None and not holder_filter(holder):
                continue
            em += stat.em
            therm += stat.thermal
            kin += stat.kinetic
            expl += stat.explosive
        total = em + therm + kin + expl
        return DamageTypesTotal(em=em, thermal=therm, kinetic=kin, explosive=expl, total=total)