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


from .base import BaseItemMixin


class DefaultEffectProxyMixin(BaseItemMixin):
    """
    Provides access to various attributes which are exposed by
    default effect of an eve type of item.
    """

    @property
    def cycle_time(self):
        default_effect = getattr(self._eve_type, 'default_effect', None)
        if default_effect is None:
            return None
        return default_effect.get_cycle_time(self)

    @property
    def cap_use(self):
        default_effect = getattr(self._eve_type, 'default_effect', None)
        if default_effect is None:
            return None
        return default_effect.get_cap_use(self)

    @property
    def optimal_range(self):
        default_effect = getattr(self._eve_type, 'default_effect', None)
        if default_effect is None:
            return None
        return default_effect.get_optimal_range(self)

    @property
    def falloff_range(self):
        default_effect = getattr(self._eve_type, 'default_effect', None)
        if default_effect is None:
            return None
        return default_effect.get_falloff_range(self)

    @property
    def tracking_speed(self):
        default_effect = getattr(self._eve_type, 'default_effect', None)
        if default_effect is None:
            return None
        return default_effect.get_tracking_speed(self)

    @property
    def fitting_usage_chance(self):
        default_effect = getattr(self._eve_type, 'default_effect', None)
        if default_effect is None:
            return None
        return default_effect.get_fitting_usage_chance(self)
