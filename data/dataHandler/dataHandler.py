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
    Abstract base class, it handles fetching 'raw' data from
    external source. Its abstract methods are named against
    data structures (usually tables) they request, returning
    iterable with rows, each row being dictionary in
    {field name: field value} format.
    """

    @abstractmethod
    def getInvtypes(self):
        ...

    @abstractmethod
    def getInvgroups(self):
        ...

    @abstractmethod
    def getDgmattribs(self):
        ...

    @abstractmethod
    def getDgmtypeattribs(self):
        ...

    @abstractmethod
    def getDgmeffects(self):
        ...

    @abstractmethod
    def getDgmtypeeffects(self):
        ...

    @abstractmethod
    def getDgmexpressions(self):
        ...

    @abstractmethod
    def getVersion(self):
        """
        Get version of data.

        Return value:
        string with version
        """
        ...
