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


import bz2
import json
import os.path
from weakref import WeakValueDictionary

from eos.data.cache.object import *
from .abc import CacheHandler
from .exception import TypeFetchError, AttributeFetchError, EffectFetchError, ModifierFetchError


class JsonCacheHandler(CacheHandler):
    """
    This cache handler implements on-disk cache store in the form
    of compressed JSON. To improve performance further, it also
    keeps loads data from on-disk cache to memory, and uses weakref
    object cache for assembled objects.

    Positional arguments:
    diskCacheFolder -- folder where on-disk cache files are stored
    name -- unique indentifier of cache, e.g. Eos instance name
    logger -- logger to use for errors
    """

    def __init__(self, disk_cache_folder, name, logger):
        self._disk_cache_file = os.path.join(disk_cache_folder, '{}.json.bz2'.format(name))
        self._logger = logger
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
        if not os.path.exists(self._disk_cache_file):
            return
        # Read JSON into local variable
        try:
            with bz2.BZ2File(self._disk_cache_file, 'r') as file:
                json_data = file.read().decode('utf-8')
                data = json.loads(json_data)
        except KeyboardInterrupt:
            raise
        # If file doesn't exist, JSON load errors occur, or
        # anything else bad happens, do not load anything
        # and leave values as initialized
        except:
            msg = 'error during reading cache'
            self._logger.error(msg, child_name='cache_handler')
        # Load data into data cache, if no errors occurred
        # during JSON reading/parsing
        else:
            self.__update_mem_cache(data)

    def get_type(self, type_id):
        type_id = int(type_id)
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
                group_id=type_data[0],
                category_id=type_data[1],
                duration_attribute_id=type_data[2],
                discharge_attribute_id=type_data[3],
                range_attribute_id=type_data[4],
                falloff_attribute_id=type_data[5],
                tracking_speed_attribute_id=type_data[6],
                fittable_non_singleton=type_data[7],
                attributes={attr_id: attr_val for attr_id, attr_val in type_data[9]},
                effects=tuple(self.get_effect(effect_id) for effect_id in type_data[8])
            )
            self.__type_obj_cache[type_id] = type_
        return type_

    def get_attribute(self, attr_id):
        attr_id = int(attr_id)
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
                max_attribute_id=attr_data[0],
                default_value=attr_data[1],
                high_is_good=attr_data[2],
                stackable=attr_data[3]
            )
            self.__attribute_obj_cache[attr_id] = attribute
        return attribute

    def get_effect(self, effect_id):
        effect_id = int(effect_id)
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
                category_id=effect_data[0],
                is_offensive=effect_data[1],
                is_assistance=effect_data[2],
                fitting_usage_chance_attribute_id=effect_data[3],
                build_status=effect_data[4],
                modifiers=tuple(self.get_modifier(modifier_id) for modifier_id in effect_data[5])
            )
            self.__effect_obj_cache[effect_id] = effect
        return effect

    def get_modifier(self, modifier_id):
        modifier_id = int(modifier_id)
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
                context=modifier_data[1],
                source_attribute_id=modifier_data[2],
                operator=modifier_data[3],
                target_attribute_id=modifier_data[4],
                location=modifier_data[5],
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
        cache_folder = os.path.dirname(self._disk_cache_file)
        if os.path.isdir(cache_folder) is not True:
            os.makedirs(cache_folder, mode=0o755)
        with bz2.BZ2File(self._disk_cache_file, 'w') as file:
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
                type_row['group_id'],
                type_row['category_id'],
                type_row['duration_attribute_id'],
                type_row['discharge_attribute_id'],
                type_row['range_attribute_id'],
                type_row['falloff_attribute_id'],
                type_row['tracking_speed_attribute_id'],
                type_row['fittable_non_singleton'],
                tuple(type_row['effects']),  # List -> tuple
                tuple(type_row['attributes'].items())  # Dictionary -> tuple
            )
        slim_data['types'] = slim_types

        slim_attribs = {}
        for attr_row in data['attributes']:
            attribute_id = attr_row['attribute_id']
            slim_attribs[attribute_id] = (
                attr_row['max_attribute_id'],
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
                effect_row['fitting_usage_chance_attribute_id'],
                effect_row['build_status'],
                tuple(effect_row['modifiers'])  # List -> tuple
            )
        slim_data['effects'] = slim_effects

        slim_modifiers = {}
        for modifier_row in data['modifiers']:
            modifier_id = modifier_row['modifier_id']
            slim_modifiers[modifier_id] = (
                modifier_row['state'],
                modifier_row['context'],
                modifier_row['source_attribute_id'],
                modifier_row['operator'],
                modifier_row['target_attribute_id'],
                modifier_row['location'],
                modifier_row['filter_type'],
                modifier_row['filter_value']
            )
        slim_data['modifiers'] = slim_modifiers

        return slim_data

    def __update_mem_cache(self, data):
        """
        Loads data into memory data cache.

        Positional arguments:
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
