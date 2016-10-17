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


"""
Original code by Entity, as seen in reverence.
"""


class CachedProperty:
    """
    Decorator class, imitates property behavior, but additionally
    caches results returned by decorated method as attribute of
    instance to which decorated method belongs. As python, when getting
    attribute with certain name, seeks for class instance's attributes
    first, then for methods, it gets cached result. To clear cache, just
    delete cached attribute.
    """

    def __init__(self, method):
        self.__method = method

    def __get__(self, instance, owner):
        # Return descriptor if called from class
        if instance is None:
            return self
        # If called from instance, execute decorated method
        # and store returned value as class attribute, which
        # has the same name as method, then return it to caller
        value = self.__method(instance)
        setattr(instance, self.__method.__name__, value)
        return value
