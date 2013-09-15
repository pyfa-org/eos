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


eosVersion = 'git'

# Keeps instance of Eos which will be used when new fits are
# created without passing Eos instance explicitly
defaultInstance = None


class Eos:
    """
    Top-level object to glue multiple things together.
    Used internally as contact point to get logger and
    fetch necessary data, thus should be passed to top-
    level objects like Fit.

    Positional arguments:
    dataHandler -- object which implements standard data
    interface (returns data rows for several tables as
    dicts and is able to get data version)

    Keyword arguments:
    cachedHandler -- cache handler implementation
    name -- name of this eos instance, used as key to
    log and cache files, thus should be unique for all
    running eos instances. Default is 'eos'.
    storagePath -- path to store various files. Default
    is ~/.eos
    """

    def __init__(self, dataHandler, cacheHandler=None, name='eos',
                 storagePath=None, makeDefault=False):
        self.__name = name
        self.__path = self.__initializePath(storagePath)
        self._logger = self.__initializeLogger()

        self.__initializeCache(dataHandler, cacheHandler)

        if makeDefault is True:
            global defaultInstance
            defaultInstance = self

    @property
    def name(self):
        return self.__name

    # Context manager methods
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    # Initialization methods
    def __initializeCacheHandler(self, cacheHandler):
        """See what has been passed to"""


    def __initializePath(self, path):
        """Process path we've received from user and return it."""
        if path is None:
            path = os.path.join('~', '.eos')
        path = os.path.expanduser(path)
        return path

    def __initializeLogger(self):
        """
        Initialize logging facilities, log few initial messages,
        and return logger.
        """
        logger = Logger(self.name, os.path.join(self.__path, 'logs'))
        logger.info('------------------------------------------------------------------------')
        logger.info('session started')
        return logger

    def __initializeCache(self, dataHandler, cacheHandler):
        """
        Check if the cache is outdated and, if necessary, compose it
        using passed datahandler and cacheHandler. If cacheHandler
        was specified as None, default on-disk JSON handler is used.
        """
        if cacheHandler is None:
            cacheHandler = JsonCacheHandler(os.path.join(self.__path, 'cache'),
                                            self.__name, self._logger)
        self._cacheHandler = cacheHandler

        # Compare fingerprints from data and cache
        cacheFp = cacheHandler.getFingerprint()
        dataVersion = dataHandler.getVersion()
        currentFp = '{}_{}_{}'.format(self.name, dataVersion, eosVersion)
        # If data version is corrupt or fingerprints mismatch,
        # update cache
        if dataVersion is None or cacheFp != currentFp:
            if dataVersion is None:
                msg = 'data version is None, updating cache'
            else:
                msg = 'fingerprint mismatch: cache "{}", data "{}", updating cache'.format(cacheFp, currentFp)
            self._logger.info(msg)
            # Generate cache, apply customizations and write it
            cacheData = CacheGenerator(self._logger).run(dataHandler)
            CacheCustomizer().runBuiltIn(cacheData)
            cacheHandler.updateCache(cacheData, currentFp)
