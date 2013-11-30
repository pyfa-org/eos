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


from .holder import HolderBase


class DefaultEffectAttribMixin(HolderBase):
    """
    Provides access to various attributes via aliases, the
    mapping between aliases and actual attributes with their
    values is provided by default effect of item..
    """

    @property
    def tracking_speed(self):
        return self.__get_item_specific_attr('tracking_speed_attribute_id')

    @property
    def optimal_range(self):
        return self.__get_item_specific_attr('range_attribute_id')

    @property
    def falloff_range(self):
        return self.__get_item_specific_attr('falloff_attribute_id')

    @property
    def cycle_time(self):
        raw_value = self.__get_item_specific_attr('duration_attribute_id')
        if raw_value is None:
            value = raw_value
        else:
            value = raw_value / 1000
        return value

    def __get_item_specific_attr(self, attr_name):
        """
        If attribute ID which we're trying to get is
        located on holder's item, this functions helps
        to fetch it.
        """
        default_effect = getattr(self.item, '_default_effect', None)
        if default_effect is None:
            return None
        attr_id = getattr(default_effect, attr_name, None)
        if attr_id is None:
            return None
        try:
            return self.attributes[attr_id]
        except KeyError:
            return None
