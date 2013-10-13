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


from eos.const.eos import Location, State
from eos.fit.holder import Holder
from eos.fit.holder.attachable_functions.misc import set_state, get_tracking_speed, get_optimal_range, \
get_falloff_range, get_cycle_time
from eos.fit.holder.attachable_functions.tanking import get_hp, get_resistances, get_ehp, get_worst_case_ehp


class Drone(Holder):
    """Single drone."""

    __slots__ = ()

    def __init__(self, type_id):
        Holder.__init__(self, type_id, State.offline)

    @property
    def _location(self):
        return Location.space

    tracking_speed = property(get_tracking_speed)
    optimal_range = property(get_optimal_range)
    falloff_range = property(get_falloff_range)
    cycle_time = property(get_cycle_time)
    hp = property(get_hp)
    resistances = property(get_resistances)
    get_ehp = get_ehp
    worst_case_ehp = property(get_worst_case_ehp)

    @Holder.state.setter
    def state(self, new_state):
        set_state(self, new_state)
