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


from ..base import BaseItemMixin


class DefaultEffectProxyMixin(BaseItemMixin):
    """Provides access to attributes which are exposed by default effect."""

    @property
    def cycle_time(self):
        return self.__safe_get_from_defeff('get_duration')

    @property
    def optimal_range(self):
        return self.__safe_get_from_defeff('get_optimal_range')

    @property
    def falloff_range(self):
        return self.__safe_get_from_defeff('get_falloff_range')

    @property
    def tracking_speed(self):
        return self.__safe_get_from_defeff('get_tracking_speed')

    def __safe_get_from_defeff(self, method):
        default_effect = self._type_default_effect
        if default_effect is None:
            return None
        return getattr(default_effect, method)(self)
