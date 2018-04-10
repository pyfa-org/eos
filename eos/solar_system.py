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


from eos.source import Source
from eos.source import SourceManager
from eos.util.default import DEFAULT


class SolarSystem:
    """Defines solar system.

    Args:
        source (optional): Source to use for fits located in this solar system.
            When not specified, source which is set as default in source manager
            will be used.
    """

    def __init__(self, source=DEFAULT):
        self.__source = None
        self.fits = set()
        # Initialize defaults
        if source is DEFAULT:
            source = SourceManager.default
        self.source = source

    @property
    def source(self):
        """Access point for solar system's source.

        Source is used to load fits' items.
        """
        return self.__source

    @source.setter
    def source(self, new_source):
        # Attempt to fetch source from source manager if passed object is not
        # instance of source class
        if not isinstance(new_source, Source) and new_source is not None:
            new_source = SourceManager.get(new_source)
        old_source = self.source
        if new_source is old_source:
            return
        for fit in self.fits:
            for item in fit._item_iter(skip_autoitems=True):
                item._unload()
        self.__source = new_source
        for fit in self.fits:
            for item in fit._item_iter(skip_autoitems=True):
                item._load()
