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

    def get_nominal_volley(self, target_resistances):
        em = 0
        therm = 0
        kin = 0
        expl = 0
        for holder in self.__dealers:
            volley = holder.get_nominal_volley(target_resistances=target_resistances)
            if volley is None:
                continue
            em += volley.em
            therm += volley.thermal
            kin += volley.kinetic
            expl += volley.explosive
        total = em + therm + kin + expl
        return DamageTypesTotal(em=em, thermal=therm, kinetic=kin, explosive=expl, total=total)

    def get_nominal_dps(self, target_resistances, reload):
        em = 0
        therm = 0
        kin = 0
        expl = 0
        for holder in self.__dealers:
            dps = holder.get_nominal_dps(target_resistances=target_resistances, reload=reload)
            if dps is None:
                continue
            em += dps.em
            therm += dps.thermal
            kin += dps.kinetic
            expl += dps.explosive
        total = em + therm + kin + expl
        return DamageTypesTotal(em=em, thermal=therm, kinetic=kin, explosive=expl, total=total)
