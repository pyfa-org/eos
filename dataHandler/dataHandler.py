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


class DataHandler:
    """
    DataHandler abstract baseclass, it handles fetching relevant data from wherever it is stored
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def getType(self, typeId):
        """Return the type with the passed id"""
        ...

    @abstractmethod
    def getAttribute(self, attrId):
        """Return the attribute with the passed id"""
        ...

    @abstractmethod
    def getEffect(self, effectId):
        """Return the effect with the passed id"""
        ...

    @abstractmethod
    def getExpression(self, expId):
        """Return the expression with the passed id"""
        ...
