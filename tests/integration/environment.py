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
    AttrFetchError, EffectFetchError, TypeFetchError)
from eos.eve_object import AttrFactory, EffectFactory, TypeFactory


TEST_ID_START = 1000000


class CacheHandler:

    def __init__(self):
        self.__type_data = {}
        self.__attr_data = {}
        self.__effect_data = {}
        self.__allocated_type_id = 0
        self.__allocated_attr_id = 0
        self.__allocated_effect_id = 0

    def mktype(self, type_id=None, customize=False, **kwargs):
        # Allocate & verify ID
        if type_id is None:
            type_id = self.allocate_type_id()
        if type_id in self.__type_data:
            raise KeyError(type_id)
        # Create, store and return type
        item_type = TypeFactory.make(
            type_id=type_id, customize=customize, **kwargs)
        self.__type_data[item_type.id] = item_type
        return item_type

    def mkattr(self, attr_id=None, **kwargs):
        # Allocate & verify ID
        if attr_id is None:
            attr_id = self.allocate_attr_id()
        if attr_id in self.__attr_data:
            raise KeyError(attr_id)
        # Create, store and return attribute
        attr = AttrFactory.make(attr_id=attr_id, **kwargs)
        self.__attr_data[attr.id] = attr
        return attr

    def mkeffect(self, effect_id=None, customize=False, **kwargs):
        # Allocate & verify ID
        if effect_id is None:
            effect_id = self.allocate_effect_id()
        if effect_id in self.__effect_data:
            raise KeyError(effect_id)
        # Create, store and return effect
        effect = EffectFactory.make(
            effect_id=effect_id, customize=customize, **kwargs)
        self.__effect_data[effect.id] = effect
        return effect

    def get_type(self, type_id):
        try:
            return self.__type_data[type_id]
        except KeyError:
            raise TypeFetchError(type_id)

    def get_attr(self, attr_id):
        try:
            return self.__attr_data[attr_id]
        except KeyError:
            raise AttrFetchError(attr_id)

    def get_effect(self, effect_id):
        try:
            return self.__effect_data[effect_id]
        except KeyError:
            raise EffectFetchError(effect_id)

    def allocate_type_id(self):
        allocated_id = max((
            TEST_ID_START - 1, self.__allocated_type_id,
            *self.__type_data.keys())) + 1
        self.__allocated_type_id = allocated_id
        return allocated_id

    def allocate_attr_id(self):
        allocated_id = max((
            TEST_ID_START - 1, self.__allocated_attr_id,
            *self.__attr_data.keys())) + 1
        self.__allocated_attr_id = allocated_id
        return allocated_id

    def allocate_effect_id(self):
        allocated_id = max((
            TEST_ID_START - 1, self.__allocated_effect_id,
            *self.__effect_data.keys())) + 1
        self.__allocated_effect_id = allocated_id
        return allocated_id
