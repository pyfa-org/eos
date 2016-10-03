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


import bz2
import json
import os.path
from logging import getLogger
from weakref import WeakValueDictionary

from eos.data.cache_object import Attribute, Effect, Modifier, Type
from eos.util.repr import make_repr_str
from .abc import BaseCacheHandler
from .exception import TypeFetchError, AttributeFetchError, EffectFetchError, ModifierFetchError


logger = getLogger(__name__)


class JsonCacheHandler(BaseCacheHandler):
    """
    This cache handler implements on-disk cache store in the form
    of compressed JSON. To improve performance further, it also
    keeps loads data from on-disk cache to memory, and uses weakref
    object cache for assembled objects.

    Required arguments:
    cache_path -- file name where on-disk cache will be stored (.json.bz2)
    """

    def __init__(self, cache_path):
        self._cache_path = cache_path
        # Initialize memory data cache
        self.__type_data_cache = {}
        self.__attribute_data_cache = {}
        self.__effect_data_cache = {}
        self.__modifier_data_cache = {}
        self.__fingerprint = None
        # Initialize weakref object cache
        self.__type_obj_cache = WeakValueDictionary()
        self.__attribute_obj_cache = WeakValueDictionary()
        self.__effect_obj_cache = WeakValueDictionary()
        self.__modifier_obj_cache = WeakValueDictionary()

        # If cache doesn't exist, silently finish initialization
        if not os.path.exists(self._cache_path):
            return
        # Read JSON into local variable
        try:
            with bz2.BZ2File(self._cache_path, 'r') as file:
                json_data = file.read().decode('utf-8')
                data = json.loads(json_data)
        except KeyboardInterrupt:
            raise
        # If file doesn't exist, JSON load errors occur, or
        # anything else bad happens, do not load anything
        # and leave values as initialized
        except:
            msg = 'error during reading cache'
            logger.error(msg)
        # Load data into data cache, if no errors occurred
        # during JSON reading/parsing
        else:
            self.__update_mem_cache(data)

    def get_type(self, type_id):
        try:
            type_id = int(type_id)
        except TypeError as e:
            raise TypeFetchError(type_id) from e
        try:
            type_ = self.__type_obj_cache[type_id]
        except KeyError:
            # We do str(int(id)) here because JSON dictionaries
            # always have strings as key
            json_type_id = str(type_id)
            try:
                type_data = self.__type_data_cache[json_type_id]
            except KeyError as e:
                raise TypeFetchError(type_id) from e
            type_ = Type(
                type_id=type_id,
                group=type_data[0],
                category=type_data[1],
                attributes={attr_id: attr_val for attr_id, attr_val in type_data[2]},
                effects=tuple(self.get_effect(effect_id) for effect_id in type_data[3]),
                default_effect=None if type_data[4] is None else self.get_effect(type_data[4])
            )
            self.__type_obj_cache[type_id] = type_
        return type_

    def get_attribute(self, attr_id):
        try:
            attr_id = int(attr_id)
        except TypeError as e:
            raise AttributeFetchError(attr_id) from e
        try:
            attribute = self.__attribute_obj_cache[attr_id]
        except KeyError:
            json_attr_id = str(attr_id)
            try:
                attr_data = self.__attribute_data_cache[json_attr_id]
            except KeyError as e:
                raise AttributeFetchError(attr_id) from e
            attribute = Attribute(
                attribute_id=attr_id,
                max_attribute=attr_data[0],
                default_value=attr_data[1],
                high_is_good=attr_data[2],
                stackable=attr_data[3]
            )
            self.__attribute_obj_cache[attr_id] = attribute
        return attribute

    def get_effect(self, effect_id):
        try:
            effect_id = int(effect_id)
        except TypeError as e:
            raise EffectFetchError(effect_id) from e
        try:
            effect = self.__effect_obj_cache[effect_id]
        except KeyError:
            json_effect_id = str(effect_id)
            try:
                effect_data = self.__effect_data_cache[json_effect_id]
            except KeyError as e:
                raise EffectFetchError(effect_id) from e
            effect = Effect(
                effect_id=effect_id,
                category=effect_data[0],
                is_offensive=effect_data[1],
                is_assistance=effect_data[2],
                duration_attribute=effect_data[3],
                discharge_attribute=effect_data[4],
                range_attribute=effect_data[5],
                falloff_attribute=effect_data[6],
                tracking_speed_attribute=effect_data[7],
                fitting_usage_chance_attribute=effect_data[8],
                build_status=effect_data[9],
                modifiers=tuple(self.get_modifier(modifier_id) for modifier_id in effect_data[10])
            )
            self.__effect_obj_cache[effect_id] = effect
        return effect

    def get_modifier(self, modifier_id):
        try:
            modifier_id = int(modifier_id)
        except TypeError as e:
            raise ModifierFetchError(modifier_id) from e
        try:
            modifier = self.__modifier_obj_cache[modifier_id]
        except KeyError:
            json_modifier_id = str(modifier_id)
            try:
                modifier_data = self.__modifier_data_cache[json_modifier_id]
            except KeyError as e:
                raise ModifierFetchError(modifier_id) from e
            modifier = Modifier(
                modifier_id=modifier_id,
                state=modifier_data[0],
                scope=modifier_data[1],
                src_attr=modifier_data[2],
                operator=modifier_data[3],
                tgt_attr=modifier_data[4],
                domain=modifier_data[5],
                filter_type=modifier_data[6],
                filter_value=modifier_data[7]
            )
            self.__modifier_obj_cache[modifier_id] = modifier
        return modifier

    def get_fingerprint(self):
        return self.__fingerprint

    def update_cache(self, data, fingerprint):
        # Make light version of data and add fingerprint
        # to it
        data = self.__strip_data(data)
        data['fingerprint'] = fingerprint
        # Update disk cache
        cache_folder = os.path.dirname(self._cache_path)
        if os.path.isdir(cache_folder) is not True:
            os.makedirs(cache_folder, mode=0o755)
        with bz2.BZ2File(self._cache_path, 'w') as file:
            json_data = json.dumps(data)
            file.write(json_data.encode('utf-8'))
        # Update data cache; encode to JSON and decode back
        # to make sure form of data is the same as after
        # loading it from cache (e.g. dictionary keys are
        # stored as strings in JSON)
        data = json.loads(json_data)
        self.__update_mem_cache(data)

    def __strip_data(self, data):
        """
        Rework passed data, keying it and stripping dictionary
        keys from rows for performance.
        """
        slim_data = {}

        slim_types = {}
        for type_row in data['types']:
            type_id = type_row['type_id']
            slim_types[type_id] = (
                type_row['group'],
                type_row['category'],
                tuple(type_row['attributes'].items()),  # Dictionary -> tuple
                tuple(type_row['effects']),  # List -> tuple
                type_row['default_effect']
            )
        slim_data['types'] = slim_types

        slim_attribs = {}
        for attr_row in data['attributes']:
            attribute_id = attr_row['attribute_id']
            slim_attribs[attribute_id] = (
                attr_row['max_attribute'],
                attr_row['default_value'],
                attr_row['high_is_good'],
                attr_row['stackable']
            )
        slim_data['attributes'] = slim_attribs

        slim_effects = {}
        for effect_row in data['effects']:
            effect_id = effect_row['effect_id']
            slim_effects[effect_id] = (
                effect_row['effect_category'],
                effect_row['is_offensive'],
                effect_row['is_assistance'],
                effect_row['duration_attribute'],
                effect_row['discharge_attribute'],
                effect_row['range_attribute'],
                effect_row['falloff_attribute'],
                effect_row['tracking_speed_attribute'],
                effect_row['fitting_usage_chance_attribute'],
                effect_row['build_status'],
                tuple(effect_row['modifiers'])  # List -> tuple
            )
        slim_data['effects'] = slim_effects

        slim_modifiers = {}
        for modifier_row in data['modifiers']:
            modifier_id = modifier_row['modifier_id']
            slim_modifiers[modifier_id] = (
                modifier_row['state'],
                modifier_row['scope'],
                modifier_row['src_attr'],
                modifier_row['operator'],
                modifier_row['tgt_attr'],
                modifier_row['domain'],
                modifier_row['filter_type'],
                modifier_row['filter_value']
            )
        slim_data['modifiers'] = slim_modifiers

        return slim_data

    def __update_mem_cache(self, data):
        """
        Loads data into memory data cache.

        Required arguments:
        data -- dictionary with data to load
        """
        self.__type_data_cache = data['types']
        self.__attribute_data_cache = data['attributes']
        self.__effect_data_cache = data['effects']
        self.__modifier_data_cache = data['modifiers']
        self.__fingerprint = data['fingerprint']
        # Also clear object cache to make sure objects composed
        # from old data are gone
        self.__type_obj_cache.clear()
        self.__attribute_obj_cache.clear()
        self.__effect_obj_cache.clear()
        self.__modifier_obj_cache.clear()

    def __repr__(self):
        spec = [['cache_path', '_cache_path']]
        return make_repr_str(self, spec)
