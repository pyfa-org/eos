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


import os.path

from eos.data.cache.customizer import CacheCustomizer
from eos.data.cache.generator import CacheGenerator
from eos.data.cache.handler import JsonCacheHandler
from eos.util.logger import Logger


EOS_VERSION = 'git'

# Keeps instance of Eos which will be used when new fits are
# created without passing Eos instance explicitly
default_instance = None


class Eos:
    """
    Top-level object to glue multiple things together.
    Used internally as contact point to get logger and
    fetch necessary data, thus should be passed to top-
    level objects like Fit.

    Positional arguments:
    data_handler -- object which implements standard data
    interface (returns data rows for several tables as
    dicts and is able to get data version)

    Keyword arguments:
    cache_handler -- cache handler implementation. If not
    specified, default JSON handler is used.
    name -- name of this eos instance, used as key to
    log and cache files, thus should be unique for all
    running eos instances. Default is 'eos'.
    storage_path -- path to store various files. Default
    is ~/.eos
    """

    def __init__(self, data_handler, cache_handler=None, name='eos',
                 storage_path=None, make_default=False):
        self.__name = name
        self.__path = self.__initialize_path(storage_path)
        self._logger = self.__initialize_logger()

        self.__initialize_cache(data_handler, cache_handler)

        if make_default is True:
            global default_instance
            default_instance = self

    @property
    def name(self):
        return self.__name

    # Context manager methods
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    # Initialization methods
    def __initialize_path(self, path):
        """Process path we've received from user and return it."""
        if path is None:
            path = os.path.join('~', '.eos')
        path = os.path.expanduser(path)
        return path

    def __initialize_logger(self):
        """
        Initialize logging facilities, log few initial messages,
        and return logger.
        """
        logger = Logger(self.name, os.path.join(self.__path, 'logs'))
        logger.info('------------------------------------------------------------------------')
        logger.info('session started')
        return logger

    def __initialize_cache(self, data_handler, cache_handler):
        """
        Check if the cache is outdated and, if necessary, compose it
        using passed data handler and cache handler. If cache handler
        was specified as None, default on-disk JSON handler is used.
        """
        if cache_handler is None:
            cache_handler = JsonCacheHandler(os.path.join(self.__path, 'cache'),
                                             self.__name, self._logger)
        self._cache_handler = cache_handler

        # Compare fingerprints from data and cache
        cache_fp = cache_handler.get_fingerprint()
        data_version = data_handler.get_version()
        current_fp = '{}_{}_{}'.format(self.name, data_version, EOS_VERSION)
        # If data version is corrupt or fingerprints mismatch,
        # update cache
        if data_version is None or cache_fp != current_fp:
            if data_version is None:
                msg = 'data version is None, updating cache'
            else:
                msg = 'fingerprint mismatch: cache "{}", data "{}", updating cache'.format(
                    cache_fp, current_fp)
            self._logger.info(msg)
            # Generate cache, apply customizations and write it
            cache_data = CacheGenerator(self._logger).run(data_handler)
            CacheCustomizer(self._logger).run_builtin(cache_data)
            cache_handler.update_cache(cache_data, current_fp)
