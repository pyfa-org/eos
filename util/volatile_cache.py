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


class VolatileProperty:
    """
    Caches attribute on instance and adds note
    about it to special set, which should be added
    by VolatileMixin.
    """

    __slots__ = ('method',)

    def __init__(self, func):
        self.method = func

    def __get__(self, inst, cls):
        if inst is None:
            return self
        else:
            value = self.method(inst)
            name = self.method.__name__
            setattr(inst, name, value)
            inst._volatile_attrs.add(name)
            return value


class VolatileMixin:
    """
    Should be added as base class for all
    classes using volatileproperty on them.
    """

    __slots__ = ('_volatile_attrs',)

    def __init__(self):
        self._volatile_attrs = set()

    def _clear_volatile_attrs(self):
        """
        Remove all the caches values which were
        stored since the last cleanup.
        """
        for attr_name in self._volatile_attrs:
            try:
                delattr(self, attr_name)
            except AttributeError:
                pass
        self._volatile_attrs.clear()
