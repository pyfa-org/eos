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


from abc import ABCMeta
from abc import abstractmethod

from eos.eve_obj.effect import Effect
from eos.stats_container import DmgStats


class DmgDealerEffect(Effect, metaclass=ABCMeta):

    # Flag which controls if this effect suppresses non-suppressor damage
    # dealers on its item
    suppress_dds = False

    @abstractmethod
    def get_volley(self, item):
        ...

    def get_dps(self, item, reload):
        cycle_parameters = self.get_cycle_parameters(item, reload)
        if cycle_parameters is None:
            return DmgStats(0, 0, 0, 0)
        volley = self.get_volley(item)
        return DmgStats(
            volley.em,
            volley.thermal,
            volley.kinetic,
            volley.explosive,
            1 / cycle_parameters.average_time)

    @abstractmethod
    def get_applied_volley(self, item, tgt_data):
        ...

    def get_applied_dps(self, item, tgt_data, reload):
        cycle_parameters = self.get_cycle_parameters(item, reload)
        if cycle_parameters is None:
            return DmgStats(0, 0, 0, 0)
        volley = self.get_applied_volley(item, tgt_data)
        dps = DmgStats(
            volley.em,
            volley.thermal,
            volley.kinetic,
            volley.explosive,
            1 / cycle_parameters.average_time)
        return dps
