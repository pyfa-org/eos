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


from logging import getLogger

from eos import __version__ as eos_version
from eos.data.eve_obj_builder import EveObjBuilder
from eos.util.repr import make_repr_str
from .exception import ExistingSourceError
from .exception import UnknownSourceError
from .source import Source


logger = getLogger(__name__)


class SourceManager:
    """Manages data sources.

    Handle and access different sources in an easy way. Useful for cases when
    you want to work with, for example, Tranquility and Singularity data at the
    same time.
    """

    # Format: {literal alias: Source}
    _sources = {}

    # Default source, will be used implicitly when instantiating fit
    default = None

    @classmethod
    def add(cls, alias, data_handler, cache_handler, make_default=False):
        """Add source to source manager.

        Adding includes initializing all facilities hidden behind name 'source'.
        After source has been added, it is accessible with alias.

        Args:
            alias: Alias under which source will be accessible.
            data_handler: Data handler instance.
            cache_handler: Cache handler instance.
            make_default (optional): Do we need to mark passed source as default
                or not. Default source will be used for instantiating new fits,
                if no other source is specified.
        """
        logger.info('adding source with alias "{}"'.format(alias))
        if alias in cls._sources:
            raise ExistingSourceError(alias)

        # Compare fingerprints from data and cache
        cache_fp = cache_handler.get_fingerprint()
        data_version = data_handler.get_version()
        current_fp = cls.__format_fingerprint(data_version)

        # If data version is corrupt or fingerprints mismatch, update cache
        if data_version is None or cache_fp != current_fp:
            if data_version is None:
                logger.info('data version is None, updating cache')
            else:
                msg = (
                    'fingerprint mismatch: cache "{}", data "{}", '
                    'updating cache'
                ).format(cache_fp, current_fp)
                logger.info(msg)

            # Generate eve objects and cache them, as generation takes
            # significant amount of time
            eve_objects = EveObjBuilder.run(data_handler)
            cache_handler.update_cache(eve_objects, current_fp)

        # Finally, add record to list of sources
        source = Source(alias=alias, cache_handler=cache_handler)
        cls._sources[alias] = source
        if make_default is True:
            cls.default = source

    @classmethod
    def get(cls, alias):
        """Using source alias, return source.

        Args:
            alias: Alias of source to return.

        Returns:
            Source instance.
        """
        try:
            return cls._sources[alias]
        except KeyError:
            raise UnknownSourceError(alias)

    @classmethod
    def remove(cls, alias):
        """Remove source by alias.

        Args:
            alias: Alias of source to remove.
        """
        logger.info('removing source with alias "{}"'.format(alias))
        try:
            del cls._sources[alias]
        except KeyError:
            raise UnknownSourceError(alias)

    @classmethod
    def list(cls):
        return list(cls._sources.keys())

    @staticmethod
    def __format_fingerprint(data_version):
        return '{}_{}'.format(data_version, eos_version)

    @classmethod
    def __repr__(cls):
        spec = [['sources', '_sources']]
        return make_repr_str(cls, spec)
