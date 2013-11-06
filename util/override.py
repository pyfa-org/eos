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


class OverrideDescriptor:
    """
    Take attribute name as argument on initialization,
    and return it on access, if override hasn't been set,
    else return override.
    """

    def __init__(self, default_name):
        self.__default_name = default_name
        self.__override_name = '_{}_{}'.format(type(self).__name__, default_name)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if hasattr(instance, self.__override_name):
            return getattr(instance, self.__override_name)
        return getattr(instance, self.__default_name)

    def __set__(self, instance, value):
        setattr(instance, self.__override_name, value)

    def __delete__(self, instance):
        try:
            delattr(instance, self.__override_name)
        except AttributeError as e:
            msg = 'override for {} is not set'.format(self.__default_name)
            raise AttributeError(msg) from e
