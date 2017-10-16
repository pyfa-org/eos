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


from eos.data.cache_handler.exception import (
    AttributeFetchError, EffectFetchError, TypeFetchError)
from eos.eve_object.attribute import Attribute
from eos.eve_object.effect import Effect
from eos.eve_object.type import Type


TEST_ID_START = 1000000


class CacheHandler:

    def __init__(self):
        self.__type_data = {}
        self.__attribute_data = {}
        self.__effect_data = {}
        self.__allocated_type = 0
        self.__allocated_attribute = 0
        self.__allocated_effect = 0

    def type(self, type_id=None, customize=False, **kwargs):
        # Allocate & verify ID
        if type_id is None:
            type_id = self.allocate_type_id()
        if type_id in self.__type_data:
            raise KeyError(type_id)
        # Create, store and return type
        eve_type = Type(type_id=type_id, customize=customize, **kwargs)
        self.__type_data[eve_type.id] = eve_type
        return eve_type

    def attr(self, attribute_id=None, **kwargs):
        # Allocate & verify ID
        if attribute_id is None:
            attribute_id = self.allocate_attr_id()
        if attribute_id in self.__attribute_data:
            raise KeyError(attribute_id)
        # Create, store and return attribute
        attribute = Attribute(attribute_id=attribute_id, **kwargs)
        self.__attribute_data[attribute.id] = attribute
        return attribute

    def effect(self, effect_id=None, customize=False, **kwargs):
        # Allocate & verify ID
        if effect_id is None:
            effect_id = self.allocate_effect_id()
        if effect_id in self.__effect_data:
            raise KeyError(effect_id)
        # Create, store and return effect
        effect = Effect(effect_id=effect_id, customize=customize, **kwargs)
        self.__effect_data[effect.id] = effect
        return effect

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

    def allocate_type_id(self):
        allocated = max((
            TEST_ID_START - 1, self.__allocated_type,
            *self.__type_data.keys())) + 1
        self.__allocated_type = allocated
        return allocated

    def allocate_attr_id(self):
        allocated = max((
            TEST_ID_START - 1, self.__allocated_attribute,
            *self.__attribute_data.keys())) + 1
        self.__allocated_attribute = allocated
        return allocated

    def allocate_effect_id(self):
        allocated = max((
            TEST_ID_START - 1, self.__allocated_effect,
            *self.__effect_data.keys())) + 1
        self.__allocated_effect = allocated
        return allocated
