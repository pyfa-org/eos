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


# TODO: in python 3.4, these's built-in enum module. Use it instead of this


class Enum(type):
    """
    We use classes as enums throughout eos, this class
    can be used as metaclass for such classes, providing
    some additional functionality.
    """

    def __new__(cls, name, bases, dict_):
        # Name map
        # Format: {value: name}
        valueNameMap = {}
        for attrName, val in dict_.items():
            if attrName.startswith('_') is True:
                continue
            if val in valueNameMap:
                raise ValueError('enum contains duplicate values')
            valueNameMap[val] = attrName
        # Assign our custom data structures to class dict
        dict_['_values'] = tuple(valueNameMap)
        dict_['_valueNameMap'] = valueNameMap
        return type.__new__(cls, name, bases, dict_)

    def __iter__(self):
        return iter(self._values)

    def __contains__(self, value):
        return self._values.__contains__(value)

    def _getName(self, value):
        return self._valueNameMap.get(value)
