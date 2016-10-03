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


from logging import getLogger
from collections import namedtuple

from eos import __version__ as eos_version
from eos.util.repr import make_repr_str
from .cache_customizer import CacheCustomizer
from .cache_generator import CacheGenerator
from .exception import ExistingSourceError, UnknownSourceError


logger = getLogger(__name__)


Source = namedtuple('Source', ('alias', 'cache_handler'))


class SourceManager:
    """
    Handle and access different sources in an easy way. Useful for cases
    when you want to work with, for example, Tranquility and Singularity
    data at the same time.
    """

    # Format:
    # {literal alias: Source}
    _sources = {}

    # Default source, will be used implicitly when instantiating fit
    default = None

    @classmethod
    def add(cls, alias, data_handler, cache_handler, make_default=False):
        """
        Add source to source manager - this includes initializing
        all facilities hidden behind name 'source'. After source
        has been added, it is accessible with alias.

        Required arguments:
        alias -- alias under which source will be accessible
        data_handler -- object which implements standard data interface
        (returns data rows for several tables as dicts and is able to
        get data version)
        cache_handler -- cache handler implementation

        Optional arguments:
        make_default -- marks passed source default; it will be used
        by default for instantiating new fits
        """
        logger.info('adding source with alias "{}"'.format(alias))
        if alias in cls._sources:
            raise ExistingSourceError(alias)
        # Compare fingerprints from data and cache
        cache_fp = cache_handler.get_fingerprint()
        data_version = data_handler.get_version()
        current_fp = '{}_{}'.format(data_version, eos_version)
        # If data version is corrupt or fingerprints mismatch, update cache
        if data_version is None or cache_fp != current_fp:
            if data_version is None:
                logger.info('data version is None, updating cache')
            else:
                msg = 'fingerprint mismatch: cache "{}", data "{}", updating cache'.format(
                    cache_fp, current_fp)
                logger.info(msg)
            # Generate cache, apply customizations and write it
            cache_data = CacheGenerator().run(data_handler)
            CacheCustomizer().run_builtin(cache_data)
            cache_handler.update_cache(cache_data, current_fp)
        # Finally, add record to list of sources
        source = Source(alias=alias, cache_handler=cache_handler)
        cls._sources[alias] = source
        if make_default is True:
            cls.default = source

    @classmethod
    def get(cls, alias):
        """
        Using source alias, return source data.

        Required arguments:
        alias -- alias of source to return

        Return value:
        (alias, edb, eos) named tuple with alias,
        SQL Alchemy database session and Eos instance for requested
        source
        """
        try:
            return cls._sources[alias]
        except KeyError:
            raise UnknownSourceError(alias)

    @classmethod
    def remove(cls, alias):
        """
        Remove source by alias.

        Required arguments:
        alias -- alias of source to remove
        """
        logger.info('removing source with alias "{}"'.format(alias))
        try:
            del cls._sources[alias]
        except KeyError:
            raise UnknownSourceError(alias)

    @classmethod
    def list(cls):
        return list(cls._sources.keys())

    @classmethod
    def __repr__(cls):
        spec = [['sources', '_sources']]
        return make_repr_str(cls, spec)
