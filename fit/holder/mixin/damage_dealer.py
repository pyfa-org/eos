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


class DamageDealerMixin:
    """
    Mixin intended to use with all entities which are able
    to deal damage (modules, drones).
    """

    def get_nominal_volley(self, target_resistances=None):
        return

    def get_volley_vs_target(self, target_data=None, target_resistances=None):
        return

    def get_chance_to_hit(self, target_data=None):
        return

    def get_nominal_dps(self, target_resistances=None, reload=True):
        return

    def get_dps_vs_target(self, target_data=None, target_resistances=None, reload=True):
        return
