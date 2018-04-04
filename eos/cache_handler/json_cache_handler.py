# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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
import os
from logging import getLogger

from eos.eve_obj.attribute import AttrFactory
from eos.eve_obj.effect import EffectFactory
from eos.eve_obj.modifier import DogmaModifier
from eos.eve_obj.type import AbilityData
from eos.eve_obj.type import TypeFactory
from eos.util.repr import make_repr_str
from .base import BaseCacheHandler
from .exception import AttrFetchError
from .exception import EffectFetchError
from .exception import TypeFetchError


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
        self.__attr_storage = {}
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

    def get_attr(self, attr_id):
        try:
            attr_id = int(attr_id)
        except TypeError as e:
            raise AttrFetchError(attr_id) from e
        try:
            attr = self.__attr_storage[attr_id]
        except KeyError as e:
            raise AttrFetchError(attr_id) from e
        return attr

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
        types, attrs, effects = eve_objects
        cache_data = {
            'types': [self.__type_compress(item_type) for item_type in types],
            'attrs': [self.__attr_compress(attr) for attr in attrs],
            'effects': [self.__effect_compress(effect) for effect in effects],
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
        self.__attr_storage.clear()
        self.__effect_storage.clear()
        # Process effects first, as item types rely on effects being available
        for effect_data in cache_data['effects']:
            effect = self.__effect_decompress(effect_data)
            self.__effect_storage[effect.id] = effect
        for type_data in cache_data['types']:
            item_type = self.__type_decompress(type_data)
            self.__type_storage[item_type.id] = item_type
        for attr_data in cache_data['attrs']:
            attr = self.__attr_decompress(attr_data)
            self.__attr_storage[attr.id] = attr
        self.__fingerprint = cache_data['fingerprint']

    # Entity compression/decompression methods
    def __type_compress(self, item_type):
        """Compress item type into python primitives."""
        if item_type.default_effect is not None:
            default_effect_id = item_type.default_effect.id
        else:
            default_effect_id = None
        type_data = (
            item_type.id,
            item_type.group_id,
            item_type.category_id,
            tuple(item_type.attrs.items()),
            tuple(item_type.effects.keys()),
            default_effect_id,
            tuple(item_type.abilities_data.items()))
        return type_data

    def __type_decompress(self, type_data):
        """Reconstruct item type from python primitives."""
        default_effect_id = type_data[5]
        if default_effect_id is None:
            default_effect = None
        else:
            default_effect = self.get_effect(default_effect_id)
        item_type = TypeFactory.make(
            type_id=type_data[0],
            group_id=type_data[1],
            category_id=type_data[2],
            attrs={k: v for k, v in type_data[3]},
            effects=tuple(self.get_effect(eid) for eid in type_data[4]),
            default_effect=default_effect,
            abilities_data={k: AbilityData(*v) for k, v in type_data[6]})
        return item_type

    def __attr_compress(self, attr):
        """Compress attribute into python primitives."""
        attr_data = (
            attr.id,
            attr.max_attr_id,
            attr.default_value,
            attr.high_is_good,
            attr.stackable)
        return attr_data

    def __attr_decompress(self, attr_data):
        """Reconstruct attribute from python primitives."""
        attr = AttrFactory.make(
            attr_id=attr_data[0],
            max_attr_id=attr_data[1],
            default_value=attr_data[2],
            high_is_good=attr_data[3],
            stackable=attr_data[4])
        return attr

    def __effect_compress(self, effect):
        """Compress effect into python primitives."""
        effect_data = (
            effect.id,
            effect.category_id,
            effect.is_offensive,
            effect.is_assistance,
            effect.duration_attr_id,
            effect.discharge_attr_id,
            effect.range_attr_id,
            effect.falloff_attr_id,
            effect.tracking_speed_attr_id,
            effect.fitting_usage_chance_attr_id,
            effect.build_status,
            tuple(
                self.__modifier_compress(m)
                for m in effect.modifiers))
        return effect_data

    def __effect_decompress(self, effect_data):
        """Reconstruct effect from python primitives."""
        effect = EffectFactory.make(
            effect_id=effect_data[0],
            category_id=effect_data[1],
            is_offensive=effect_data[2],
            is_assistance=effect_data[3],
            duration_attr_id=effect_data[4],
            discharge_attr_id=effect_data[5],
            range_attr_id=effect_data[6],
            falloff_attr_id=effect_data[7],
            tracking_speed_attr_id=effect_data[8],
            fitting_usage_chance_attr_id=effect_data[9],
            build_status=effect_data[10],
            modifiers=tuple(
                self.__modifier_decompress(md)
                for md in effect_data[11]))
        return effect

    def __modifier_compress(self, modifier):
        """Compress dogma modifier into python primitives."""
        modifier_data = (
            modifier.tgt_filter,
            modifier.tgt_domain,
            modifier.tgt_filter_extra_arg,
            modifier.tgt_attr_id,
            modifier.operator,
            modifier.src_attr_id)
        return modifier_data

    def __modifier_decompress(self, modifier_data):
        """Reconstruct dogma modifier from python primitives."""
        modifier = DogmaModifier(
            tgt_filter=modifier_data[0],
            tgt_domain=modifier_data[1],
            tgt_filter_extra_arg=modifier_data[2],
            tgt_attr_id=modifier_data[3],
            operator=modifier_data[4],
            src_attr_id=modifier_data[5])
        return modifier

    # Auxiliary methods
    def __repr__(self):
        spec = [['cache_path', '_cache_path']]
        return make_repr_str(self, spec)
