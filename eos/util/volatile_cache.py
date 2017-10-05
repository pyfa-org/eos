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


class volatile_property:
    """Decorator which caches call result and provides facilities to clear it.

    Adds note on cached result to special set which is used by volatile mixins
    to clear cache.
    """

    def __init__(self, method):
        self.__method = method

    def __get__(self, instance, _):
        if instance is None:
            return self
        value = self.__method(instance)
        name = self.__method.__name__
        setattr(instance, name, value)
        instance._volatile_attrs.add(name)
        return value


class InheritableVolatileMixin:
    """Inheritable volatile cache mixin.

    Should be added as parent class for all classes using volatile property on
    them. This mixin is for classical inheritance trees.
    """

    def __init__(self):
        self._volatile_attrs = set()

    def _clear_volatile_attrs(self):
        for attr_name in self._volatile_attrs:
            try:
                delattr(self, attr_name)
            except AttributeError:
                pass
        self._volatile_attrs.clear()


class CooperativeVolatileMixin:
    """Cooperative volatile cache mixin.

    Should be added as parent class for all classes using volatile property on
    them. This mixin is for cooperative-style inheritance.

    Cooperative methods:
        __init__
    """

    def __init__(self, **kwargs):
        self._volatile_attrs = set()
        super().__init__(**kwargs)

    def _clear_volatile_attrs(self):
        for attr_name in self._volatile_attrs:
            try:
                delattr(self, attr_name)
            except AttributeError:
                pass
        self._volatile_attrs.clear()
