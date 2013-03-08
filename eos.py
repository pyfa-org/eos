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

from eos.data.cacheCustomizer import CacheCustomizer
from eos.data.cacheHandler import JsonCacheHandler
from eos.data.cacheGenerator import CacheGenerator
from eos.util.logger import Logger


eosVersion = 'git'


class Eos:
    """
    Top-level object to glue multiple things together.
    Used internally as contact point to get logger and
    fetch necessary data, thus should be passed to top-
    level objects like Fit.

    Positional arguments:
    dataHandler -- object which implements standard data
    interface (returns data rows for several table as
    dicts and is able to get data version)

    Optional arguments:
    name -- name of this eos instance, used as key to
    log and cache files, thus should be unique for all
    running eos instances. Default is 'eos'.
    storagePath -- path to store various files. Default
    is ~/.eos
    """

    def __init__(self, dataHandler, name='eos', storagePath=None):
        self.__name = name
        self.__path = self.__initializePath(storagePath)
        self._logger = self.__initializeLogger()
        self._cacheHandler = self.__initializeData(dataHandler)

    @property
    def name(self):
        return self.__name

    # Context manager methods
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    # Initialization methods
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

    def __initializeData(self, dataHandler):
        """
        Using passed dataHandler, compose on-disk cache if
        necessary, load this cache in memory and return
        cache handler which deals with it.
        """
        cacheHandler = JsonCacheHandler(os.path.join(self.__path, 'cache'), self.name, self._logger)
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
        return cacheHandler
