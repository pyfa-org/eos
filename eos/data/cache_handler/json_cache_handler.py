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


import bz2
import json
import os.path
from logging import getLogger
from weakref import WeakValueDictionary

from eos.data.cachable import *
from eos.data.cachable.custom import customize_effect, customize_type
from eos.util.repr import make_repr_str
from .base import BaseCacheHandler
from .exception import TypeFetchError, AttributeFetchError, EffectFetchError


logger = getLogger(__name__)


class JsonCacheHandler(BaseCacheHandler):
    """
    This cache handler implements persistent cache store in the form
    of compressed JSON. To improve performance further, it also keeps
    loaded data in memory, and uses weakref object cache for assembled
    objects.

    Required arguments:
    cache_path -- file path where persistent cache will be stored (.json.bz2)
    """

    def __init__(self, cache_path):
        self._cache_path = os.path.abspath(cache_path)
        # Initialize memory data cache
        self.__type_data_cache = {}
        self.__attribute_data_cache = {}
        self.__effect_data_cache = {}
        self.__fingerprint = None
        # Initialize weakref object cache
        self.__type_obj_cache = WeakValueDictionary()
        self.__attribute_obj_cache = WeakValueDictionary()
        self.__effect_obj_cache = WeakValueDictionary()
        # Fill memory cache with data, if possible
        self.__load_persistent_cache()

    def get_type(self, type_id):
        try:
            type_id = int(type_id)
        except TypeError as e:
            raise TypeFetchError(type_id) from e
        try:
            eve_type = self.__type_obj_cache[type_id]
        except KeyError:
            try:
                type_data = self.__type_data_cache[type_id]
            except KeyError as e:
                raise TypeFetchError(type_id) from e
            eve_type = Type.decompress(self, type_data)
            customize_type(eve_type)
            self.__type_obj_cache[type_id] = eve_type
        return eve_type

    def get_attribute(self, attr_id):
        try:
            attr_id = int(attr_id)
        except TypeError as e:
            raise AttributeFetchError(attr_id) from e
        try:
            attribute = self.__attribute_obj_cache[attr_id]
        except KeyError:
            try:
                attr_data = self.__attribute_data_cache[attr_id]
            except KeyError as e:
                raise AttributeFetchError(attr_id) from e
            attribute = Attribute.decompress(self, attr_data)
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
            try:
                effect_data = self.__effect_data_cache[effect_id]
            except KeyError as e:
                raise EffectFetchError(effect_id) from e
            effect = Effect.decompress(self, effect_data)
            customize_effect(effect)
            self.__effect_obj_cache[effect_id] = effect
        return effect

    def get_fingerprint(self):
        return self.__fingerprint

    def __load_persistent_cache(self):
        # If cache file doesn't exist, bail out - we have nothing to read
        if not os.path.exists(self._cache_path):
            return
        try:
            with bz2.BZ2File(self._cache_path, 'r') as file:
                json_cache_data = file.read().decode('utf-8')
                cache_data = json.loads(json_cache_data)
        except KeyboardInterrupt:
            raise
        # If file doesn't exist, JSON load errors occurs, or anything else bad
        # happens, leave memory cache empty
        except:
            msg = 'error during reading cache'
            logger.error(msg)
        # Load cache data into memory data cache, if everything went smooth
        else:
            self.__update_memory_cache(cache_data)

    def update_cache(self, cachable_data, fingerprint):
        """
        Replace existing cache data with passed data.
        """
        types, attributes, effects = cachable_data
        cache_data = {
            'types': {type_id: eve_type.compress() for type_id, eve_type in types.items()},
            'attributes': {attr_id: attr.compress() for attr_id, attr in attributes.items()},
            'effects': {effect_id: effect.compress() for effect_id, effect in effects.items()},
            'fingerprint': fingerprint
        }
        self.__update_persistent_cache(cache_data)
        self.__update_memory_cache(cache_data)

    def __update_persistent_cache(self, cache_data):
        """
        Write passed data to persistent storage, possibly
        overwriting existing data.
        """
        cache_folder = os.path.dirname(self._cache_path)
        if os.path.isdir(cache_folder) is not True:
            os.makedirs(cache_folder, mode=0o755)
        with bz2.BZ2File(self._cache_path, 'w') as file:
            json_cache_data = json.dumps(cache_data)
            file.write(json_cache_data.encode('utf-8'))

    def __update_memory_cache(self, cache_data):
        """
        Replace existing memory cache data with passed data.
        """
        # Convert keys to ints because we accept cache data decoded
        # from JSON, and in JSON map keys are always strings
        self.__type_data_cache = {int(k): v for k, v in cache_data['types'].items()}
        self.__attribute_data_cache = {int(k): v for k, v in cache_data['attributes'].items()}
        self.__effect_data_cache = {int(k): v for k, v in cache_data['effects'].items()}
        self.__fingerprint = cache_data['fingerprint']
        # Also clear object cache to make sure objects composed
        # from old data are gone
        self.__type_obj_cache.clear()
        self.__attribute_obj_cache.clear()
        self.__effect_obj_cache.clear()

    def __repr__(self):
        spec = [['cache_path', '_cache_path']]
        return make_repr_str(self, spec)
