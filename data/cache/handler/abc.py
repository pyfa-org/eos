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


from abc import ABCMeta
from abc import abstractmethod


class CacheHandler(metaclass=ABCMeta):
    """
    Abstract base class for cache handlers. Most of
    its methods (type, attribute, effect and modifier
    getters) should return "assembled" objects for
    use in Eos; fingerprint is single string.
    """


    @abstractmethod
    def getType(self, typeID):
        ...

    @abstractmethod
    def getAttribute(self, attrID):
        ...

    @abstractmethod
    def getEffect(self, effectID):
        ...

    @abstractmethod
    def getModifier(self, modifierID):
        ...

    @abstractmethod
    def getFingerprint(self):
        ...

    @abstractmethod
    def updateCache(self, data, fingerprint):
        """
        Update cache with passed data.

        Positional arguments:
        data -- format: {entity type: [{field name: field value}]
        fingerprint -- unique ID of data in the form of string
        """
        ...
