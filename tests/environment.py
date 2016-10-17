# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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


from eos.data.cache_handler.exception import TypeFetchError, AttributeFetchError, EffectFetchError
from eos.data.cache_object import Attribute, Effect, Type


class CacheHandler:

    def __init__(self):
        self.__type_data = {}
        self.__attribute_data = {}
        self.__effect_data = {}

    def type_(self, **kwargs):
        type_ = Type(**kwargs)
        if type_.id in self.__type_data:
            raise KeyError(type_.id)
        self.__type_data[type_.id] = type_
        return type_

    def attribute(self, **kwargs):
        attr = Attribute(**kwargs)
        if attr.id in self.__attribute_data:
            raise KeyError(attr.id)
        self.__attribute_data[attr.id] = attr
        return attr

    def effect(self, **kwargs):
        eff = Effect(**kwargs)
        if eff.id in self.__effect_data:
            raise KeyError(eff.id)
        self.__effect_data[eff.id] = eff
        return eff

    def get_type(self, type_id):
        try:
            return self.__type_data[type_id]
        except KeyError:
            raise TypeFetchError(type_id)

    def get_attribute(self, attr):
        try:
            return self.__attribute_data[attr]
        except KeyError:
            raise AttributeFetchError(attr)

    def get_effect(self, eff_id):
        try:
            return self.__effect_data[eff_id]
        except KeyError:
            raise EffectFetchError(eff_id)
