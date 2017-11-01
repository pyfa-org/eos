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


import bz2
import json
import os.path
from logging import getLogger

from eos.eve_object.attribute import Attribute
from eos.eve_object.effect import Effect
from eos.eve_object.type import Type
from eos.util.repr import make_repr_str
from .base import BaseCacheHandler
from .exception import AttributeFetchError, EffectFetchError, TypeFetchError


logger = getLogger(__name__)


class JsonCacheHandler(BaseCacheHandler):
    """JSON cache storage implementation.

    This cache handler implements persistent cache store in the form of
    compressed JSON. When data is loaded, eve objects are stored in memory, thus
    it provides extremely fast access, but has subpar initialization time and
    memory consumption.

    Args:
        cache_path: File path where persistent cache will be stored (.json.bz2).
    """

    def __init__(self, cache_path):
        self._cache_path = os.path.abspath(cache_path)
        # Initialize storage for objects
        self.__type_storage = {}
        self.__attribute_storage = {}
        self.__effect_storage = {}
        self.__fingerprint = None
        # Fill memory cache with data, if possible
        self.__load_persistent_cache()

    def get_type(self, type_id):
        try:
            type_id = int(type_id)
        except TypeError as e:
            raise TypeFetchError(type_id) from e
        try:
            item_type = self.__type_storage[type_id]
        except KeyError as e:
            raise TypeFetchError(type_id) from e
        return item_type

    def get_attribute(self, attr_id):
        try:
            attr_id = int(attr_id)
        except TypeError as e:
            raise AttributeFetchError(attr_id) from e
        try:
            attribute = self.__attribute_storage[attr_id]
        except KeyError as e:
            raise AttributeFetchError(attr_id) from e
        return attribute

    def get_effect(self, effect_id):
        try:
            effect_id = int(effect_id)
        except TypeError as e:
            raise EffectFetchError(effect_id) from e
        try:
            effect = self.__effect_storage[effect_id]
        except KeyError as e:
            raise EffectFetchError(effect_id) from e
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

    def update_cache(self, eve_objects, fingerprint):
        types, attributes, effects = eve_objects
        cache_data = {
            'types': [item_type.compress() for item_type in types],
            'attributes': [attr.compress() for attr in attributes],
            'effects': [effect.compress() for effect in effects],
            'fingerprint': fingerprint}
        self.__update_persistent_cache(cache_data)
        self.__update_memory_cache(cache_data)

    def __update_persistent_cache(self, cache_data):
        """Write passed data to persistent storage."""
        cache_folder = os.path.dirname(self._cache_path)
        if os.path.isdir(cache_folder) is not True:
            os.makedirs(cache_folder, mode=0o755)
        with bz2.BZ2File(self._cache_path, 'w') as file:
            json_cache_data = json.dumps(cache_data)
            file.write(json_cache_data.encode('utf-8'))

    def __update_memory_cache(self, cache_data):
        """Replace existing memory cache data with passed data."""
        # Clear storage to make sure objects composed from old data are gone
        self.__type_storage.clear()
        self.__attribute_storage.clear()
        self.__effect_storage.clear()
        # Process effects first, as item types rely on effects being available
        for effect_data in cache_data['effects']:
            effect = Effect.decompress(self, effect_data)
            self.__effect_storage[effect.id] = effect
        for type_data in cache_data['types']:
            item_type = Type.decompress(self, type_data)
            self.__type_storage[item_type.id] = item_type
        for attribute_data in cache_data['attributes']:
            attribute = Attribute.decompress(self, attribute_data)
            self.__attribute_storage[attribute.id] = attribute
        self.__fingerprint = cache_data['fingerprint']

    def __repr__(self):
        spec = [['cache_path', '_cache_path']]
        return make_repr_str(self, spec)
