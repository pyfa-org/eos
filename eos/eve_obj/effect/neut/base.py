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


class BaseNeutEffect(Effect, metaclass=ABCMeta):

    @abstractmethod
    def get_neut_amount(self, item):
        ...

    def get_nps(self, item, reload):
        cycle_parameters = self.get_cycle_parameters(item, reload)
        if cycle_parameters is None:
            return 0
        return self.get_neut_amount(item) / cycle_parameters.average_time
