#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2012 Anton Vorobyov
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


class DataHandler(metaclass=ABCMeta):
    """
    DataHandler abstract baseclass, it handles fetching relevant data
    from wherever it is stored.
    """

    @abstractmethod
    def getType(self, typeId):
        """
        Get Type object from data source.

        Positional arguments:
        typeId -- ID of type to get

        Return value:
        eve.type.Type object
        """
        ...

    @abstractmethod
    def getAttribute(self, attrId):
        """
        Get Attribute object from data source.

        Positional arguments:
        attrId -- ID of attribute to get

        Return value:
        eve.attribute.Attribute object
        """
        ...

    @abstractmethod
    def getEffect(self, effectId):
        """
        Get Effect object from data source.

        Positional arguments:
        effectId -- ID of effect to get

        Return value:
        eve.effect.Effect object
        """
        ...

    @abstractmethod
    def getExpression(self, expId):
        """
        Get Expression object from data source.

        Positional arguments:
        expId -- ID of expression to get

        Return value:
        eve.expression.Expression object
        """
        ...
