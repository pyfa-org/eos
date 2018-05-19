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


from math import sqrt

from eos.calculator.service import CalculationService
from eos.const.eve import AttrId
from eos.source import Source
from eos.source import SourceManager
from eos.util.default import DEFAULT
from eos.util.repr import make_repr_str
from .exception import ItemSolarSystemMismatchError
from .fit_set import FitSet


class SolarSystem:
    """Defines solar system.

    Args:
        source (optional): Source to use for fits located in this solar system.
            When not specified, source which is set as default in source manager
            will be used.
    """

    def __init__(self, source=DEFAULT):
        self.__source = None
        self._calculator = CalculationService(self)
        self.fits = FitSet(self)
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
        if old_source is not None:
            for fit in self.fits:
                fit._unload_items()
        self.__source = new_source
        if new_source is not None:
            for fit in self.fits:
                fit._load_items()

    def get_ctc_range(self, item1, item2):
        """Calculate center-to-center range between two items."""
        try:
            item1_ss = item1._fit.solar_system
        except AttributeError:
            item1_ss = None
        try:
            item2_ss = item2._fit.solar_system
        except AttributeError:
            item2_ss = None
        if item1_ss is not self or item2_ss is not self:
            msg = 'both passed items must belong to this solar system'
            raise ItemSolarSystemMismatchError(msg)
        ctc_range = sqrt(
            (item1.x - item2.x) ** 2 +
            (item1.y - item2.y) ** 2 +
            (item1.z - item2.z) ** 2)
        return ctc_range

    def get_sts_range(self, item1, item2):
        """Calculate surface-to-surface range between two items."""
        ctc_range = self.get_ctc_range(item1, item2)
        item1_radius = item1._type_attrs.get(AttrId.radius, 0)
        item2_radius = item2._type_attrs.get(AttrId.radius, 0)
        return max(0, ctc_range - item1_radius - item2_radius)

    def __repr__(self):
        spec = ['source', 'fits']
        return make_repr_str(self, spec)
